import json
import time
import asyncpg
from .models import Product


def normalize_dsn(value):
    return value.replace('postgresql+asyncpg://', 'postgresql://', 1).replace('postgres://', 'postgresql://', 1)


class PostgresStorage:
    @classmethod
    async def connect(cls, url):
        self = cls()
        self.pool = await asyncpg.create_pool(normalize_dsn(url), min_size=1, max_size=5, command_timeout=15)
        try:
            async with self.pool.acquire() as c:
                await c.execute('''
                    CREATE TABLE IF NOT EXISTS ph_preferences(user_id BIGINT PRIMARY KEY, data TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS ph_history(id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL, query TEXT NOT NULL, ts DOUBLE PRECISION NOT NULL);
                    CREATE INDEX IF NOT EXISTS ph_history_user ON ph_history(user_id,ts);
                    CREATE TABLE IF NOT EXISTS ph_favorites(id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL, url TEXT NOT NULL, data TEXT NOT NULL, UNIQUE(user_id,url));
                    CREATE TABLE IF NOT EXISTS ph_updates(update_id BIGINT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
                ''')
                # Single webhook worker. Preserve pending updates across deploys.
                await c.execute("UPDATE ph_updates SET status='pending' WHERE status='processing'")
                await c.execute("DELETE FROM ph_updates WHERE status='done' AND created_at < NOW()-INTERVAL '7 days'")
            return self
        except BaseException:
            await self.pool.close()
            raise

    async def settings(self, user):
        raw = await self.pool.fetchval('SELECT data FROM ph_preferences WHERE user_id=$1', user)
        return json.loads(raw) if raw else {'stores': [], 'budget': None, 'sort': 'relevance'}

    async def update(self, user, **values):
        data = await self.settings(user)
        data.update(values)
        await self.pool.execute('INSERT INTO ph_preferences VALUES($1,$2) ON CONFLICT(user_id) DO UPDATE SET data=EXCLUDED.data', user,json.dumps(data))
        return data

    async def remember(self, user, query):
        async with self.pool.acquire() as c, c.transaction():
            await c.execute('DELETE FROM ph_history WHERE user_id=$1 AND query=$2',user,query)
            await c.execute('INSERT INTO ph_history(user_id,query,ts) VALUES($1,$2,$3)',user,query,time.time())
            await c.execute('DELETE FROM ph_history WHERE user_id=$1 AND id NOT IN (SELECT id FROM ph_history WHERE user_id=$1 ORDER BY ts DESC LIMIT 10)',user)

    async def history(self,user):
        return [(r['id'],r['query']) for r in await self.pool.fetch('SELECT id,query FROM ph_history WHERE user_id=$1 ORDER BY ts DESC LIMIT 10',user)]

    async def favorites(self,user):
        return [(r['id'],Product(**json.loads(r['data']))) for r in await self.pool.fetch('SELECT id,data FROM ph_favorites WHERE user_id=$1 ORDER BY id DESC LIMIT 50',user)]

    async def favorite(self,user,product):
        async with self.pool.acquire() as c, c.transaction():
            await c.execute('SELECT pg_advisory_xact_lock($1)',user)
            row=await c.fetchval('SELECT id FROM ph_favorites WHERE user_id=$1 AND url=$2',user,product.url)
            if row:
                await c.execute('DELETE FROM ph_favorites WHERE user_id=$1 AND id=$2',user,row)
                return False
            count=await c.fetchval('SELECT COUNT(*) FROM ph_favorites WHERE user_id=$1',user)
            if count>=50:
                raise ValueError('Лимит — 50 товаров. Удалите ненужные из избранного.')
            await c.execute('INSERT INTO ph_favorites(user_id,url,data) VALUES($1,$2,$3)',user,product.url,json.dumps(product.to_dict()))
            return True

    async def clear(self,user):
        async with self.pool.acquire() as c, c.transaction():
            for table in ('ph_history','ph_favorites','ph_preferences'):
                await c.execute(f'DELETE FROM {table} WHERE user_id=$1',user)

    async def enqueue(self, update_id, payload):
        await self.pool.execute('INSERT INTO ph_updates(update_id,payload) VALUES($1,$2) ON CONFLICT DO NOTHING',update_id,payload)

    async def next_update(self):
        return await self.pool.fetchrow("""UPDATE ph_updates SET status='processing',attempts=attempts+1
            WHERE update_id=(SELECT update_id FROM ph_updates WHERE status='pending' ORDER BY update_id LIMIT 1 FOR UPDATE SKIP LOCKED)
            RETURNING update_id,payload,attempts""")

    async def finish_update(self,update_id,status):
        # Remove user content once successfully handled; retain id for deduplication.
        await self.pool.execute("UPDATE ph_updates SET status=$2,payload=CASE WHEN $2='done' THEN '{}' ELSE payload END WHERE update_id=$1",update_id,status)

    async def health(self):
        await self.pool.fetchval('SELECT 1')

    async def close(self):
        await self.pool.close()
