"""Record live SQL reference values without claiming Desktop visual validation."""
from datetime import datetime,timezone
from pathlib import Path
import json
import psycopg
from investment_fund_analytics.database_loading import connection_settings


def run(root):
    settings=connection_settings(root/'.env.app')
    with psycopg.connect(**settings,row_factory=psycopg.rows.dict_row) as conn:
        server=conn.execute('SELECT version() version,current_database() database,current_user login').fetchone()
        reference={}
        for name in ('pbi_performance_snapshot','pbi_risk_snapshot','pbi_quality_summary','pbi_source_lineage'):
            reference[name]=conn.execute('SELECT * FROM analytics.'+name+' ORDER BY instrument_id').fetchall()
        for name,column,dates in (
            ('pbi_daily_performance','date_key',['2021-09-30','2023-12-01','2026-09-30']),
            ('pbi_monthly_returns','date_key',['2021-09-01','2022-12-01','2026-09-01']),
            ('pbi_calendar_year_returns','date_key',['2021-01-01','2024-01-01','2026-01-01']),
            ('pbi_drawdowns','date_key',['2022-09-29','2023-09-28','2026-09-30']),
            ('pbi_rolling_63','date_key',['2023-12-04','2026-09-30']),
            ('pbi_rolling_252','date_key',['2023-12-04','2026-09-30'])):
            reference[name]=conn.execute('SELECT * FROM analytics.'+name+' WHERE '+column+'=ANY(%s::date[]) ORDER BY instrument_id,date_key',(dates,)).fetchall()
    evidence=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  connection=dict(host=settings['host'],port=settings['port'],database=server['database'],login=server['login']),
                  server_version=server['version'],status='SQL reference only; Power BI engine not evaluated',reference=reference)
    folder=root/'data/processed/powerbi';folder.mkdir(parents=True,exist_ok=True)
    (folder/'desktop_validation_reference.json').write_text(json.dumps(evidence,indent=2,default=str)+'\n',encoding='utf-8')
    # Deliberately whitelist only non-secret connection fields.
    print(json.dumps(dict(connection=evidence['connection'],server_version=server['version'],
                         reference_rows={key:len(value) for key,value in reference.items()}),indent=2))
    lines=['# Power BI build and validation status','',
           'Checked '+evidence['checked_at_utc']+'. User-reported five-page completion and manual review are recorded separately in reports/powerbi_validation.md. This generated report contains SQL reference values only; it does not inspect PBIX contents or evaluate Desktop DAX, visuals or interactions. DWS publication permission remains unresolved and redistribution restricted; keep this numerical report local.','',
           '## Confirmed live connection','',
           f"Server `{settings['host']}:{settings['port']}`; database `{server['database']}`; Database authentication login `{server['login']}`. Use the corresponding password privately from `.env.app` in Desktop. No password is embedded in this report, M or command output. The root `.env` is the maintenance configuration; Desktop should use the documented project login instead.",'',
           'Server: '+server['version']+'.','',
           '## Database-facing validation','',
           'This run queries snapshot, quality, lineage and representative series reference values. It does not itself re-run every key/reconciliation assertion from powerbi_validation. Its output does not certify Desktop import, DAX evaluation or visual values. Prior validation evidence is recorded separately.','',
           '| Fund | Cumulative NAV change | CAGR | Observed maximum drawdown | Volatility | Zero-target downside | VaR 95 | ES 95 | Latest rolling 63 / 252 |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    performance={r['instrument_id']:r for r in reference['pbi_performance_snapshot']}
    for r in reference['pbi_risk_snapshot']:
        p=performance[r['instrument_id']]
        lines.append(f"| Instrument {r['instrument_id']} | {float(p['cumulative_return']):.6%} | {float(p['cagr']):.6%} | {float(p['max_drawdown']):.6%} | {float(r['annualized_volatility']):.6%} | {float(r['downside_deviation']):.6%} | {float(r['var_95']):.6%} | {float(r['expected_shortfall_95']):.6%} | {float(r['latest_volatility_63']):.6%} / {float(r['latest_volatility_252']):.6%} |")
    lines+=['','Instrument 1 is bond LU0290355717; instrument 2 is equity LU0380865021. Performance boundaries 2021-09-30–2026-09-30; controlled-risk boundaries 2023-12-01–2026-09-30. Eligible/tail counts are retrieved from local SQL snapshots; rolling window parameters are 63/252 observations. Annualization is sqrt(252); downside target zero; VaR/ES refer to variable-calendar-length valuation intervals.','',
            '## Page-by-page Desktop validation register','',
            '| Page | Required card/chart checks against recorded SQL references | Actual Desktop result |',
            '| --- | --- | --- |',
            '| Executive Overview | Cumulative return, CAGR, MDD, volatility, VaR, ES, latest 63/252, sample count and data-as-of; single-fund guards and separate fixed windows | User reports completion/manual review; not independently inspected by this routine |',
            '| Performance Comparison | Rebased NAV at first/last/control-window boundary, cumulative series; Sep 2021 null monthly return, Dec 2022 caveat, Sep 2026 complete-month result; 2024 yearly return and 2021/2026 full-year nulls | User reports completion/manual review; not independently inspected by this routine |',
            '| Risk & Drawdowns | Drawdowns at equity 2022-09-29 and bond 2023-09-28; max peak/trough/recovery/status/duration; rolling warm-up nulls and latest volatility/counts; VaR/ES tail counts | User reports completion/manual review; not independently inspected by this routine |',
            '| Fund Detail | ISIN, issuer, domicile, currency, accumulating policy, benchmark metadata only; individual snapshot values and actual window labels | User reports completion/manual review; not independently inspected by this routine |',
            '| Data Quality & Methodology | Observed coverage, calendar classifications and eligibility counts from local SQL; lineage/checksums/acquisition time; refresh UTC and suppressed metrics | User reports completion/manual review; not independently inspected by this routine |','',
            '## DAX, relationships and filters','',
            'Approved DAX definitions remain in powerbi/measures.dax; no new financial measure or formula was introduced. **DAX differences: not assessable**, because no Power BI engine was run. **Relationship/filter issues: not assessed in Desktop**; this routine queries reference values, while dimension/grain assertions are performed separately by powerbi_validation. The required model is single-direction 1:* DimFund→facts and DimDate→six dated series/period facts, without fact-to-fact joins. Fixed snapshots/quality/lineage have only DimFund relationships. Chart date slicers cannot imply recomputed snapshots, rebasing or drawdown peaks. Test both-fund card blanks and all slicer/drill-through interactions in Desktop.','',
            '## Evidence and remaining work','',
            'Exact raw SQL values and representative chart points are saved locally in data/processed/powerbi/desktop_validation_reference.json. Compare Desktop values before rounding to tolerance 1e-10; do not substitute these reference values for actual Power BI output. The user reports completing and reviewing the dashboard. This routine does not independently compile DAX, authenticate Desktop refresh, inspect the saved PBIX or validate visual/filter behavior; no screenshot/PDF is generated here. Derived values and previews are not automatically cleared for publication. No benchmark/cash-relative claims or ML were added.','',
            'Follow docs/powerbi_build_guide.md for reproduction and refresh; preserve the separately maintained manual review record. Microsoft documents PBIX/PBIP conversion through Desktop File > Save as, not programmatic conversion: [official project documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).']
    (folder/'sql_reference_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':run(Path(__file__).resolve().parents[2])
