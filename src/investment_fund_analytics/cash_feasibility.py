"""Small ECB access probes only; no cash integration or risk ratios."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import pandas as pd
import requests


def run(root):
    folder=root/'data/raw/cash_feasibility'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder.mkdir(parents=True,exist_ok=True)
    results=[]
    for key in ('B.EU000A2X2A25.WT','B.EU000A2QQF08.CI'):
        for start,end in [('2023-12-01','2023-12-06'),('2026-09-25','2026-09-30')]:
            response=requests.get('https://data-api.ecb.europa.eu/service/data/EST/'+key,
                                  params=dict(startPeriod=start,endPeriod=end,format='csvdata'),timeout=30)
            if not response.ok:
                results.append(dict(series=key,url=response.url,http_status=response.status_code,
                                    retrieved_at=datetime.now(timezone.utc).isoformat(),status='access_failed'))
                (folder/'manifest.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
                continue
            response.raise_for_status()
            data=pd.read_csv(io.BytesIO(response.content))
            if not {'TIME_PERIOD','OBS_VALUE'}.issubset(data):raise ValueError('Unexpected ECB schema')
            path=folder/f'{key}_{start}.csv';path.write_bytes(response.content)
            results.append(dict(series=key,url=response.url,retrieved_at=datetime.now(timezone.utc).isoformat(),
                                sha256=hashlib.sha256(response.content).hexdigest(),raw_file=str(path.relative_to(root)),
                                rows=len(data),columns=list(data),observations=data[['TIME_PERIOD','OBS_VALUE']].to_dict('records')))
            (folder/'manifest.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    (folder/'manifest.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))


if __name__=='__main__':run(Path(__file__).resolve().parents[2])
