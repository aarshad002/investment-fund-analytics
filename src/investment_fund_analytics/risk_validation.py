"""Apply approved SQL and independently reconcile Python eligibility and metrics."""
from investment_fund_analytics.calendar_validation import read_register
import json
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from investment_fund_analytics.database_loading import connection_settings
from investment_fund_analytics.risk import interval_series,summarize,rolling


def run(root):
    gaps = pd.DataFrame(read_register(root), columns=['isin', 'gap_date', 'classification', 'reason', 'evidence_codes', 'reviewed_on'])
    with psycopg.connect(**connection_settings(root/'.env.owner'),autocommit=True) as conn:
        for name in ('controlled_intervals.sql','risk_views.sql'):
            conn.execute((root/'sql'/name).read_text(encoding='utf-8'))
    output=root/'data/processed/risk';output.mkdir(parents=True,exist_ok=True)
    errors=[];summaries=[];checks=0
    def compare(a,b):
        nonlocal checks
        checks+=1
        if a is None or pd.isna(b):
            assert a is None and pd.isna(b)
        else:
            error=abs(float(a)-float(b));assert error<=1e-10
            errors.append(error)
    with psycopg.connect(**connection_settings(root/'.env.app'),row_factory=psycopg.rows.dict_row) as conn:
        for isin in ('LU0380865021','LU0290355717'):
            nav=pd.DataFrame(conn.execute('SELECT observation_date,nav,quality_status FROM analytics.daily_nav WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall())
            closures=gaps.loc[(gaps['isin']==isin)&(gaps.classification=='expected/non-valuation day'),'gap_date']
            intervals=interval_series(nav,closures)
            sql_intervals=conn.execute('SELECT * FROM analytics.nav_intervals WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall()
            assert len(intervals)==len(sql_intervals)
            for a,b in zip(sql_intervals,intervals.to_dict('records')):
                assert a['proposed_interval_status']==b['proposed_interval_status'];checks+=1
                compare(a['interval_days'],b['interval_days'])
            metrics=summarize(intervals.loc[intervals.eligible,'observed_interval_return'])
            sql=conn.execute('SELECT * FROM analytics.controlled_risk_summary WHERE isin=%s',(isin,)).fetchone()
            for key,value in metrics.items():
                if key=='status':assert sql[key]==value;checks+=1
                else:compare(sql[key],value)
            eligible=intervals.loc[intervals.eligible]
            assert pd.Timestamp(sql['start_date'])==eligible.previous_date.min()
            assert pd.Timestamp(sql['end_date'])==eligible.observation_date.max()
            sql_rolling=conn.execute('SELECT * FROM analytics.controlled_rolling_volatility WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall()
            for window in (63,252):
                result=rolling(intervals,window)
                for a,b in zip(sql_rolling,result.to_dict('records')):
                    compare(a[f'count_{window}'],b['valid_count']);compare(a[f'volatility_{window}'],b['volatility'])
                result.to_csv(output/f'{isin}_rolling_{window}.csv',index=False)
                metrics[f'latest_volatility_{window}']=float(result.volatility.iloc[-1])
                metrics[f'latest_count_{window}']=int(result.valid_count.iloc[-1])
                metrics[f'rolling_results_{window}']=int(result.volatility.notna().sum())
            intervals.to_csv(output/f'{isin}_intervals.csv',index=False)
            summaries.append(dict(isin=isin,start_date=str(sql['start_date']),end_date=str(sql['end_date']),
                                  exclusions=intervals.proposed_interval_status.value_counts().to_dict(),**metrics))
    evidence=dict(methodology='approved-controlled-nav-v1-zero-target',comparisons=checks,
                  maximum_absolute_error=max(errors),tolerance=1e-10,summary=summaries)
    (output/'validation.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2))
    return evidence


if __name__=='__main__':run(Path(__file__).resolve().parents[2])
