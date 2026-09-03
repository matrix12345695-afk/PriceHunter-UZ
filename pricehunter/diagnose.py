"""Render Shell: python -m pricehunter.diagnose 'Iphone 17 pro max'. No tokens printed."""
import asyncio
import json
import sys
from datetime import datetime, timezone
from .service import SearchService, select_products
from .providers import MARKETS

async def main(query):
    service=SearchService()
    try:
        results,_=await service.search(query)
        report={'checked_at':datetime.now(timezone.utc).isoformat(),'query':query,'markets':[]}
        for r in results:
            report['markets'].append({'name':MARKETS[r.store].name,'status':r.status,
                'detail':r.detail,'raw_count':len(r.products),'matching_count':len(select_products([r],query)),
                'sample':[p.to_dict() for p in select_products([r],query)[:2]]})
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        await service.close()

if __name__=='__main__':
    asyncio.run(main(' '.join(sys.argv[1:]) or 'Iphone 17 pro max'))
