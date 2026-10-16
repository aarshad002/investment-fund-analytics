# Local Power BI build guide

This guide prepares a five-page Desktop report from validated PostgreSQL outputs. The user has completed and manually reviewed the five-page local PBIX. This guide describes rebuilding/refreshing it, not a new independent Desktop validation. Codex has not inspected PBIX internals or exercised its interactions. No ML or unverified cash/benchmark metrics are included. Power BI Desktop is installed according to the user. Record its actual version, PBIX revision/checksum and manual-review date; those artifact details are not independently verified here.

## Prepare views and connect

1. Start local PostgreSQL 18.6. From repository root run:

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m investment_fund_analytics.powerbi_validation
```

This applies presentation views as the existing owner using .env.owner, checks grain/relationships and exact snapshot reuse, and writes local Git-ignored CSVs in data/processed/powerbi/. It does not alter validated financial calculations or source data. Credentials are never printed. Existing roles/databases must already be configured according to environment_setup.md.

2. Open Power BI Desktop (64-bit). Home > Get data > More > Database > PostgreSQL database. Server `localhost:5432` (use the actual local port if changed); database `investment_fund_analytics`. Choose **Import**, not DirectQuery. Follow [Microsoft connector documentation](https://learn.microsoft.com/en-us/power-query/connectors/postgresql); modern Desktop includes its PostgreSQL provider, while old releases may require the documented provider installation. Do not install an arbitrary Npgsql version.
3. Select Database authentication and privately enter the existing ifa_app credentials from the local .env.app. Desktop does not automatically read .env files. Do not paste credentials into SQL, M queries or documentation. This existing loader role can insert core data; for report-only deployment prefer a DBA-provisioned SELECT-only login limited to these views. Desktop only issues read queries here. If a local connection reports no encryption support, use the connector's documented unencrypted-local option only for localhost, or configure the local server certificate; record the tested setting.
4. Navigator > analytics: select all twelve pbi_* views listed in powerbi_data_model.md, **not** raw core tables, benchmark levels or other analytics views. Transform data, rename to DimFund/DimDate/FactDaily/FactMonthly/FactYear/FactDrawdown/FactPerformance/FactRisk/FactRolling63/FactRolling252/FactQuality/FactLineage. Set types/formats using powerbi_field_mapping.md. Date columns must be Date, not Date/Time. Close & Apply. Import full available rows; do not truncate risk inputs before rolling calculations.
5. Create a blank Power Query named RefreshInfo (Advanced Editor):

```powerquery
let
    Stamp = DateTimeZone.RemoveZone(DateTimeZone.FixedUtcNow()),
    Output = #table(type table [refreshed_at_utc = datetime], {{Stamp}})
in Output
```

Load it as a disconnected one-row table. This marks model refresh evaluation UTC, not raw acquisition or data-as-of.

## Model configuration

Disable Auto date/time and relationship autodetection in File > Options and settings > Options > Current File (Data Load). Remove automatically inferred relationships. In Model view create active 1:* Single relationships from DimFund[instrument_id] to every fact[instrument_id]; from DimDate[date_key] to the six time-series/period facts specified in powerbi_data_model.md. Snapshots, quality and lineage connect only to DimFund. Do not create fact-to-fact or extra date links. Mark DimDate as date table on date_key. Sort month_name by month_number. Hide technical keys. Set numeric financial columns Don't summarize. Create measures individually from powerbi/measures.dax and apply percentage/date/count formats. DAX financial totals are intentionally blank across multiple funds/dates.

## Page 1 — Executive Overview

Use a single-select DimFund[fund_name] slicer (Select all off), default equity. Add fixed Performance Window Label and Risk Window Label above their card groups. Performance cards: Cumulative NAV Return, CAGR, Maximum Drawdown. Controlled risk cards: Annualized Volatility, Historical VaR 95, Historical ES 95, Latest Rolling 63/252, with Risk Sample Count and zero-target downside in a supporting table. Add Data As Of and Model Refresh UTC. Include a small Rebased NAV line using DimDate[date_key] and Rebased NAV, with fund name legend. Add a Between slicer called **Chart date window**; explain 'Chart dates only; snapshot cards retain the labelled windows'. Its interaction applies to the line, not snapshot cards. Do not imply all cards share a common five-year risk window. Show full snapshot start/end dates on cards/tooltips.

## Page 2 — Performance Comparison

Fund slicer allows both approved funds. Between chart-date slicer synchronized with Page 1 for time-series only. Line charts: DimDate[date_key], Rebased NAV and Cumulative Series, DimFund[fund_name] legend. Label base 100 at 2021-09-30; filtering does not reset the base. Monthly heatmap: matrix with calendar_year rows, month_name columns, Monthly NAV Return values and red/neutral/blue background formatting; require a separate single-fund slicer for the matrix or fund as an outer row group. Disable totals and show blank incomplete periods. Calendar-year grouped columns: calendar_year, Calendar Year NAV Return, fund legend; 2021/2026 full-year blanks remain blank. Fixed common-window table: fund, FactPerformance boundaries/observations and approved performance measures; disable its chart-date interactions. These categories are not peers; compare descriptively, do not rank. Status/boundary dates appear in period tooltips.

## Page 3 — Risk & Drawdowns

Single-fund slicer. Drawdown line: date_key and Observed Drawdown. Rolling lines: date_key with Rolling 63 Volatility and Rolling 252 Volatility; use the original nullable series without interpolation/fill. Controlled charts default to December 2023 onward; drawdown may display full history but must state its distinct observed-path window. Fixed cards/table: max drawdown, peak/trough/recovery dates, recovery_status, duration/ongoing days from FactPerformance; VaR/ES, sample/tail count, latest rolling counts from FactRisk. Label tail losses 'per eligible NAV valuation interval', not uniform calendar-day losses. Chart-date slicer must not reset drawdown peaks or change fixed snapshot cards. Show zero-target downside and approximate 252 interval annualization notes.

## Page 4 — Fund Detail

Set drill-through on DimFund[isin], keep all filters off unless deliberately tested; show Back button and single-fund slicer. Table fields: ISIN/name/issuer/category/domicile/currency/income policy/hedging/benchmark_name and benchmark_status. Domicile LU is independent of exchange listing. Include fixed performance/risk measures and both window labels, plus NAV/performance chart. Benchmark name is metadata only; explicit note 'benchmark-relative results unavailable'. Add methodology_notes and links to source/methodology documentation. No index chart or implied benchmark outperformance.

## Page 5 — Data Quality & Methodology

Fund slicer may allow both. Tables by fund: FactQuality observation_count, first_nav_date, last_nav_date, flagged_nav_count, absent_weekdays, expected_closures, likely_legitimate_gaps, unresolved_gaps, risk_eligible_count, outside_risk_window_count, no_prior_count and risk_excluded_issue_count. Do not call absent weekdays missing NAVs. Lineage table: fund, original source/run IDs, retrieved_at, checksum, source_url and pipeline_version. Display source redistribution restrictions, methodology notes, suppressed_metrics, model-refresh UTC and latest NAV date. Keep unresolved equity benchmark discrepancy and cash integration visibly outstanding. No independent-calendar-certified coverage percentage is invented.

## Validation before saving PBIX

The automated database-facing preparation checks have passed: all twelve view grains are unique, fund/date references are complete and snapshot fields exactly match their source views. This does not substitute for the Desktop interaction/visual checks below. Period visuals show whole SQL-precomputed months/years; disable chart Between-slicer interactions with monthly/year visuals and use dedicated year/month selections instead, so a midmonth date slice cannot be presented as a newly calculated monthly return.

Refresh all tables locally. Use pgAdmin Query Tool against project DB to run:

```sql
SELECT * FROM analytics.pbi_performance_snapshot ORDER BY instrument_id;
SELECT * FROM analytics.pbi_risk_snapshot ORDER BY instrument_id;
SELECT * FROM analytics.pbi_quality_summary ORDER BY instrument_id;
SELECT instrument_id,date_key,period_return,status
FROM analytics.pbi_monthly_returns
WHERE date_key IN ('2021-09-01','2022-12-01','2026-09-01')
ORDER BY instrument_id,date_key;
```

Compare each selected fund against its approved SQL snapshots and quality records in the same local refresh. Performance boundaries are 2021-09-30 to 2026-09-30; controlled-risk boundaries are 2023-12-01 to 2026-09-30. Verify sample counts and the actual rolling/tail counts from SQL. Match unrounded values at absolute tolerance 1e-10, then check displayed percentage rounding. Actual KPI reference values and empirical tail counts are withheld pending permission; detailed pre-redaction references are preserved locally. Do not hard-code missing values or infer a public acquisition right from this validation procedure.

Test selecting each fund and both funds: snapshot cards require one; comparison series remain separate; no sum of returns. Change chart-date range: charts clip without rebasing; fixed cards/windows stay clearly labelled. Verify September 2021 monthly blank; full calendar years 2021/2026 blank; December 2022 caveat; warm-up rolling blanks; recovered equity vs ongoing bond with null recovery date. Inspect negative drawdown axes, count vs percentage formats, tooltip dates and lineage. Repeat refresh and check unchanged values. Record Desktop version, actual refresh UTC, artifact revision and manual validation results as evidence of the user-completed dashboard; independent SQL checks do not establish direct PBIX inspection. Retain screenshots locally pending rights review.

Save locally as powerbi/Investment_Fund_Analytics.pbix (Git-ignored). PBIX embeds imported data: source publication permission remains unresolved and redistribution restricted. Do not publish it or exports until the permission basis is established. Derived values, charts, screenshots and PDFs are not automatically cleared for publication. No cloud gateway is needed for local Desktop refresh. Local CSVs are a fallback, using the same model mapping after explicit type conversion; they do not live-refresh SQL. The user reports Desktop build/manual review complete. Independent PBIX-content validation, exact version/revision evidence and artifact-publication rights review remain distinct outstanding items; SQL preparation alone does not prove them.
