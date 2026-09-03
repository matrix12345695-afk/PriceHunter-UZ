import json
import sqlite3
import time
from pathlib import Path
from .models import Product


class Storage:
    """Small local database. One event-loop thread; short, bounded transactions."""
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=10)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS preferences(user INTEGER PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, user INTEGER NOT NULL, query TEXT NOT NULL, ts REAL NOT NULL);
            CREATE INDEX IF NOT EXISTS history_user ON history(user, ts);
            CREATE TABLE IF NOT EXISTS favorites(id INTEGER PRIMARY KEY, user INTEGER NOT NULL, url TEXT NOT NULL, data TEXT NOT NULL, UNIQUE(user,url));
        ''')
        self.db.commit()

    def settings(self, user):
        row = self.db.execute('SELECT data FROM preferences WHERE user=?', (user,)).fetchone()
        return json.loads(row[0]) if row else {'stores': [], 'budget': None, 'sort': 'relevance'}

    def update(self, user, **values):
        data = self.settings(user)
        data.update(values)
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO preferences VALUES(?,?)', (user, json.dumps(data)))
        return data

    def remember(self, user, query):
        with self.db:
            self.db.execute('DELETE FROM history WHERE user=? AND query=?', (user, query))
            self.db.execute('INSERT INTO history(user,query,ts) VALUES(?,?,?)', (user, query, time.time()))
            self.db.execute('DELETE FROM history WHERE user=? AND id NOT IN (SELECT id FROM history WHERE user=? ORDER BY ts DESC LIMIT 10)', (user, user))

    def history(self, user):
        return self.db.execute('SELECT id,query FROM history WHERE user=? ORDER BY ts DESC LIMIT 10', (user,)).fetchall()

    def favorite(self, user, product):
        with self.db:
            existing = self.db.execute('SELECT id FROM favorites WHERE user=? AND url=?', (user, product.url)).fetchone()
            if existing:
                self.db.execute('DELETE FROM favorites WHERE id=? AND user=?', (existing[0], user))
                return False
            if len(self.favorites(user)) >= 50:
                raise ValueError('Лимит — 50 товаров. Удалите ненужные из избранного.')
            self.db.execute('INSERT INTO favorites(user,url,data) VALUES(?,?,?)', (user, product.url, json.dumps(product.to_dict())))
        return True

    def favorites(self, user):
        return [(row[0], Product(**json.loads(row[1]))) for row in self.db.execute('SELECT id,data FROM favorites WHERE user=? ORDER BY id DESC LIMIT 50', (user,))]

    def clear(self, user):
        with self.db:
            for table in ('history', 'favorites', 'preferences'):
                self.db.execute(f'DELETE FROM {table} WHERE user=?', (user,))

    def close(self):
        self.db.close()
