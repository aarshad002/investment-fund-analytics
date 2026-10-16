"""Apply approved performance views and reconcile all local SQL/Python outputs."""
from investment_fund_analytics.calendar_validation import read_register
from pathlib import Path
import csv
import json
import math
import pandas as pd
import psycopg
from investment_fund_analytics.database_loading import connection_settings
from investment_fund_analytics.performance import calculate,period_returns

TOLERANCE=1e-10


def reconcile(sql_value,python_value,key):
    if sql_value is None or python_value is None or pd.isna(python_value):
        assert sql_value is None and (python_value is None or pd.isna(python_value)),key
        return 0.0
    if key.endswith('_date') or key in {'period_start','period_end'}:
        assert pd.Timestamp(sql_value)==pd.Timestamp(python_value),key
        return 0.0
    if isinstance(sql_value,str):
        assert sql_value==python_value,key
        return 0.0
    error=abs(float(sql_value)-float(python_value))
    assert math.isfinite(error) and error<=TOLERANCE,(key,error)
    return error


def run(root):
    gaps = read_register(root)
    with psycopg.connect(**connection_settings(root/'.env.owner'),autocommit=True) as owner:
        owner.execute((root/'sql/performance_views.sql').read_text(encoding='utf-8'))
    output=root/'data/processed/performance';output.mkdir(parents=True,exist_ok=True)
    errors=[];summaries=[];monthly=[];annual=[];series_count=0
    with psycopg.connect(**connection_settings(root/'.env.app'),autocommit=True,row_factory=psycopg.rows.dict_row) as conn:
        comparisons=conn.execute('SELECT * FROM analytics.common_window_comparison ORDER BY isin').fetchall()
        for comparison in comparisons:
            isin=comparison['isin']
            raw=conn.execute('SELECT observation_date,nav,quality_status FROM analytics.daily_nav WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall()
            frame=pd.DataFrame(raw)
            window=frame.loc[pd.to_datetime(frame.observation_date).between(pd.Timestamp(comparison['start_date']),pd.Timestamp(comparison['end_date']))]
            metrics,path=calculate(window)
            for key,value in metrics.items():errors.append(reconcile(comparison[key],value,key))
            sql_path=conn.execute('SELECT observation_date,drawdown FROM analytics.drawdown_series WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall()
            for s,p in zip(sql_path,path.itertuples()):
                errors.append(reconcile(s['observation_date'],p.observation_date,'observation_date'))
                errors.append(reconcile(s['drawdown'],p.drawdown,'drawdown'))
            assert len(sql_path)==len(path);series_count+=len(path)
            cumulative=conn.execute('SELECT cumulative_return FROM analytics.cumulative_return WHERE isin=%s ORDER BY observation_date',(isin,)).fetchall()
            expected=pd.to_numeric(frame.nav).astype(float)/float(frame.nav.iloc[0])-1
            for s,p in zip(cumulative,expected):errors.append(reconcile(s['cumulative_return'],p,'cumulative_return'))
            summaries.append(dict(isin=isin,**metrics,basis='native EUR accumulating NAV change',
                                  drawdown_basis='observed path; unobserved losses/recovery may be missed',
                                  calendar_status='calendar_caveat'))
            fund_output=dict(summaries[-1])
            for frequency,target in [('month',monthly),('year',annual)]:
                python=period_returns(frame,frequency,[g for g in gaps if g['isin']==isin])
                sql_rows=conn.execute('SELECT * FROM analytics.period_returns WHERE isin=%s AND period_type=%s ORDER BY period_start',(isin,frequency)).fetchall()
                assert len(sql_rows)==len(python)
                for s,p in zip(sql_rows,python.to_dict('records')):
                    for key,value in p.items():errors.append(reconcile(s[key],value,key))
                    target.append(dict(isin=isin,**p))
                fund_output['monthly_returns' if frequency=='month' else 'calendar_year_returns']=python.astype(object).where(pd.notna(python),None).to_dict('records')
            path.to_csv(output/f'{isin}_drawdown.csv',index=False)
            (output/f'{isin}_performance.json').write_text(json.dumps(fund_output,indent=2,default=str,allow_nan=False)+'\n',encoding='utf-8')
    for name,records in [('summary',summaries),('monthly_returns',monthly),('calendar_year_returns',annual)]:
        pd.DataFrame(records).to_csv(output/f'{name}.csv',index=False)
    evidence=dict(methodology='phase4-observed-nav-v1',tolerance=TOLERANCE,maximum_absolute_error=max(errors),
                  reconciled_values=len(errors),drawdown_rows=series_count,monthly_rows=len(monthly),annual_rows=len(annual),
                  summary=summaries)
    (output/'validation.json').write_text(json.dumps(evidence,indent=2,default=str)+'\n',encoding='utf-8')
    lines=['# Performance analysis validation','',
           'Methodology: phase4-observed-nav-v1. SQL analytical views applied to the local project database; Python outputs independently reconciled against them. Returns are native EUR accumulating NAV changes, not certified corporate-action-adjusted total returns.','',
           '| ISIN | Start | End | Cumulative NAV change | CAGR | Observed maximum drawdown | Peak | Trough | Recovery |',
           '| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |']
    for s in summaries:
        lines.append(f"| {s['isin']} | {s['start_date'].date()} | {s['end_date'].date()} | {s['cumulative_return']:.2%} | {s['cagr']:.2%} | {s['max_drawdown']:.2%} | {s['peak_date'].date() if s['peak_date'] is not None else 'N/A'} | {s['trough_date'].date() if s['trough_date'] is not None else 'N/A'} | {s['recovery_status']}: {s['recovery_date'].date() if s['recovery_date'] is not None else 'not observed'} |")
    lines+=['','Recovery dates/status and durations are recorded in the generated local summaries; null recovery dates/durations remain unavailable rather than zero.','',
            '## Tests','',
            'This reconciliation run does not execute pytest or establish a suite total. The 16 October 2026 audit separately recorded 66 passed, zero failed/skipped. Existing performance tests cover: known compounding, constant values, tied peak/trough/recovery, unrecovered duration, incomplete months, prior-month boundary, leap/nonleap one-year gates, missing observations, missing/stale period boundaries, and invalid/duplicate dates or NAVs.','']
    lines+=['','## SQL/Python reconciliation','',
            f"All {len(errors):,} comparisons passed at absolute tolerance {TOLERANCE:g}; maximum absolute numeric error {max(errors):.3g}. Checked both summaries, all {series_count:,} drawdown dates/values, cumulative series, all {len(monthly)} monthly and {len(annual)} annual records, including boundaries, status and null eligibility. No daily-risk metric was calculated.",'',
            '## Boundary and calendar policy','',
            'Monthly SQL returns compound successive observed NAV ratios via a sum of logarithms. Python uses the independent endpoint ratio; interior omissions do not prevent endpoint NAV-change measurement. Each period starts at the last preceding observation and ends at its last observation. No forward-filling occurs. Missing preceding-period boundaries or an unfinished period yield a null period_return, with observed_return retained separately as a partial-window diagnostic. Seven calendar days is a conservative boundary-age screen, not an invented expected valuation calendar. Calendar review/unresolved gap labels remain attached even when the endpoint return is available. No period is labelled calendar-certified complete.','',
            'September 2021 lacks a preceding boundary; its monthly return is suppressed. Calendar years 2021 and 2026 are partial and their full-year returns are suppressed; observed partial returns remain separately labelled. December 2022 and calendar year 2022 retain an unresolved_gap label. CAGR requires a calendar anniversary and uses elapsed days/365.25. Comparison uses identical actual shared endpoints; equity and bond are compared descriptively, not ranked as peers.','',
            'Drawdown is computed only on observed NAVs, with its peak reset at the common-window start. Tied peaks use the latest peak preceding the earliest worst trough. Recovery is the first observed later NAV at or above that peak; duration is calendar days from peak. Unrecovered episodes have null recovery dates/durations and a separately labelled ongoing elapsed duration. Missing NAVs can hide deeper losses or an earlier recovery, so reported observed maximum drawdown is a lower bound on loss magnitude along the unobserved path. It is not a calendar-certified daily-risk statistic.','',
            '## Outputs and reproduction','',
            'Local Git-ignored outputs: data/processed/performance/summary.csv, monthly_returns.csv, calendar_year_returns.csv, each fund drawdown CSV and combined performance JSON (summary plus all monthly/year records), and validation.json. Source/run lineage remains in daily_nav and the core database. SQL views remain live, so rerun reconciliation after new data.','',
            '```powershell',"$env:PYTHONPATH = 'src'",'.\\.venv\\Scripts\\python.exe -m investment_fund_analytics.performance_validation','.\\.venv\\Scripts\\python.exe -m pytest -q','```','',
            '## Suppressed and deferred metrics','',
            'This routine reconciles performance only. Six controlled NAV-only risk metrics are implemented separately for the approved restricted window; Sharpe, Sortino and benchmark-relative metrics remain disabled. The calendar caveat, historical transition and native-NAV adjustment semantics remain limitations. Five Power BI pages are user-completed/manually reviewed, without independent PBIX inspection by this routine. No ML is implemented. DWS source publication permission is unresolved and redistribution restricted, including derived values and screenshots; keep this numerical report local.','']
    (output/'performance_analysis_validation.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(evidence,indent=2,default=str))
    return evidence


if __name__=='__main__':run(Path.cwd())
