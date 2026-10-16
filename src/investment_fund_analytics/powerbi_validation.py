"""Apply presentation views, validate grains, and export local refresh-ready CSVs."""
from pathlib import Path
import json
import pandas as pd
import psycopg
from investment_fund_analytics.database_loading import connection_settings

KEYS={
 'pbi_fund_overview':['instrument_id'], 'pbi_date':['date_key'],
 'pbi_daily_performance':['instrument_id','date_key'],
 'pbi_monthly_returns':['instrument_id','date_key'],
 'pbi_calendar_year_returns':['instrument_id','date_key'],
 'pbi_drawdowns':['instrument_id','date_key'],
 'pbi_performance_snapshot':['instrument_id','window_key','date_key'],
 'pbi_risk_snapshot':['instrument_id','window_key','date_key'],
 'pbi_rolling_63':['instrument_id','date_key'],
 'pbi_rolling_252':['instrument_id','date_key'],
 'pbi_quality_summary':['instrument_id','date_key'],
 'pbi_source_lineage':['instrument_id','ingestion_run_id']}


def run(root):
    with psycopg.connect(**connection_settings(root/'.env.owner'),autocommit=True) as conn:
        conn.execute((root/'sql/powerbi_views.sql').read_text(encoding='utf-8'))
    folder=root/'data/processed/powerbi';folder.mkdir(parents=True,exist_ok=True)
    counts={};frames={}
    with psycopg.connect(**connection_settings(root/'.env.app'),row_factory=psycopg.rows.dict_row) as conn:
        for view,keys in KEYS.items():
            frame=pd.DataFrame(conn.execute('SELECT * FROM analytics.'+view).fetchall())
            assert not frame.empty and not frame[keys].isna().any().any() and not frame.duplicated(keys).any(),view
            frames[view]=frame;counts[view]=len(frame)
            frame.to_csv(folder/(view+'.csv'),index=False)
        fund_ids=set(frames['pbi_fund_overview'].instrument_id)
        dates=set(frames['pbi_date'].date_key)
        for name,frame in frames.items():
            if 'instrument_id' in frame:assert set(frame.instrument_id)<=fund_ids,name
            if 'date_key' in frame:assert set(frame.date_key)<=dates,name
        performance=frames['pbi_performance_snapshot'].set_index('instrument_id')
        risk=frames['pbi_risk_snapshot'].set_index('instrument_id')
        for view,parent,fields in [('pbi_performance_snapshot','common_window_comparison',
             ['cumulative_return','cagr','max_drawdown']),('pbi_risk_snapshot','controlled_risk_summary',
             ['annualized_volatility','downside_deviation','var_95','expected_shortfall_95','valid_count'])]:
            expected=pd.DataFrame(conn.execute('SELECT * FROM analytics.'+parent).fetchall()).set_index('instrument_id')
            actual=frames[view].set_index('instrument_id')
            for field in fields:assert actual[field].to_dict()==expected[field].to_dict(),field
        raw_counts={
            row['instrument_id']: row['n'] for row in conn.execute("SELECT instrument_id,count(*) AS n FROM core.observation WHERE instrument_id=ANY(%s) GROUP BY instrument_id", (list(fund_ids),)).fetchall()}
        assert frames['pbi_quality_summary'].set_index('instrument_id').observation_count.to_dict()==raw_counts
        for view,frequency in [('pbi_monthly_returns','month'),('pbi_calendar_year_returns','year')]:
            expected=conn.execute("SELECT count(*) AS n FROM analytics.period_returns WHERE period_type=%s AND period_return IS NULL",(frequency,)).fetchone()['n']
            assert frames[view].period_return.isna().sum()==expected
    evidence=dict(counts=counts,unique_keys=True,dimension_integrity=True,
                  exact_snapshot_reconciliation=True,pbix_visual_validation='not independently inspected; user-reported completion documented separately in reports/powerbi_validation.md')
    (folder/'validation.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2))
    return evidence


if __name__=='__main__':run(Path(__file__).resolve().parents[2])
