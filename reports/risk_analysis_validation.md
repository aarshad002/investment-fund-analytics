# Controlled observed-NAV risk validation

Validated 7 October 2026. Restricted user approval covers six NAV-only metrics. Methodology: approved-controlled-nav-v1-zero-target. This is controlled observed-NAV analysis, not unrestricted five-year daily-risk analysis.

## Withheld results

Source-derived numerical financial results are withheld from this working-tree candidate pending redistribution permission. Exact pre-redaction documents are preserved in a verified Git-ignored local archive. Successful private SQL/Python verification is recorded here as procedural evidence; this summary does not publish the underlying results or grant a reader permission to acquire or redistribute them.

The private checks covered annualized volatility, zero-target downside deviation, historical VaR/expected shortfall and both rolling-volatility windows. Metric values, empirical tail counts and observed rolling-output totals are withheld. Fixed analysis boundaries remain 2023-12-01 to 2026-09-30; these identify methodology scope rather than a published risk result. Individual valid counts and warm-up statuses remain in local outputs for authorized verification.

## Calendar and exclusions

**Zero** flagged-boundary or unexplained-gap exclusions occur within the approved window. Fifteen expected post-change omitted weekdays are accepted closures. Any other missing weekday excludes its spanning interval. No NAV filling, zero insertion, date shifting or bridging of excluded observations occurs.

Both actual boundary dates and calendar-day interval lengths are preserved in SQL and CSV. Weekends/confirmed closures remain one valuation interval with variable elapsed-day horizons. Equity historical calendar-amendment timing remains a limitation. This operational approval does not resolve the unresolved historical omission or certify the full five-year calendar.

## Definitions

Volatility uses sample standard deviation (ddof=1) times sqrt(252). **NAV-only downside deviation uses zero return as target:** sqrt(mean(min(return,0)^2)) times sqrt(252), averaging over all eligible observations. It is distinct from the deferred cash-target specification and uses no implicit cash return.

Annualization assumes approximately 252 valuation intervals/year, without correcting variable calendar horizons or statistical dependence. Returns are native EUR accumulating NAV changes, not independently certified corporate-action-adjusted total returns. VaR is minus the linear-interpolated 5th percentile. Expected shortfall is minus the mean at/below that cutoff, including ties. Signed results are not clipped. Tail metrics describe observed eligible valuation intervals, not fixed one-calendar-day losses or regulatory risk.

Summary minimum sample is 252. Rolling windows require all 63/252 original consecutive interval rows eligible; excluded rows are not compressed away. Every metric preserves valid counts; tail counts are additional to full sample size.

## Reconciliation and tests

SQL/Python **15,146 comparisons passed**, absolute tolerance 1e-10, maximum absolute numerical difference **4.996003610813204e-16**. Python independently builds calendar eligibility from original NAVs and the CSV gap register. Checks include all classifications/elapsed lengths, summary metrics/counts/status/tail counts and every rolling count/value/null; actual boundary dates are separately checked. SQL uses stddev_samp, percentile_cont and physical ROWS windows; Python uses NumPy and pandas.

The original restricted-risk checkpoint recorded passing tests, including deterministic cases for known volatility, zero-target downside, linear VaR, tied-tail expected shortfall, both rolling windows with gap barriers, constant/positive-only values, insufficient/invalid inputs, weekday/weekend/holiday classification, flagged-boundary non-bridging and fixed-window end enforcement. Prior live source/database/benchmark/performance tests also pass. The approved window will not silently expand if later observations are loaded.

## Reproduction and outputs

SQL: sql/controlled_intervals.sql and sql/risk_views.sql. Python: src/investment_fund_analytics/risk.py and risk_validation.py. Git-ignored data/processed/risk/ contains validation.json and each fund's original interval records and rolling_63/rolling_252 CSVs. Source observations/lineage are unchanged.

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m investment_fund_analytics.risk_validation
.\.venv\Scripts\python.exe -m pytest -q
```

## Separate validation gates

See [cash/benchmark investigation](../docs/cash_benchmark_validation.md). Sharpe, Sortino, correlation, beta, tracking error and information ratio remain unimplemented. Benchmark candidates retain flags, four missing values each and unresolved equity discrepancy. The five-page Power BI dashboard is user-completed/manually reviewed, without independent PBIX inspection here. No ML is implemented. Public numerical results remain withheld; see [publication review](../docs/publication_review.md).
