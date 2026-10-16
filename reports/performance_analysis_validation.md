# Performance analysis validation

Methodology: phase4-observed-nav-v1. SQL analytical views applied to the local project database; Python outputs independently reconciled against them. Returns are native EUR accumulating NAV changes, not certified corporate-action-adjusted total returns.

## Withheld results

Source-derived numerical financial results are withheld from this working-tree candidate pending redistribution permission. Exact pre-redaction documents are preserved in a verified Git-ignored local archive. Successful private SQL/Python verification is recorded here as procedural evidence; this summary does not publish the underlying results or grant a reader permission to acquire or redistribute them.

The private review found an observed recovery for the equity fund and an ongoing unrecovered episode for the bond fund. Return/CAGR/drawdown values, peak/trough/recovery dates and episode durations are withheld. Recovery is observed-path evidence, not proof of an uninterrupted historical path.

## Tests

The original performance-stage checkpoint recorded passing tests covering: known compounding, constant values, tied peak/trough/recovery, unrecovered duration, incomplete months, prior-month boundary, leap/nonleap one-year gates, missing observations, missing/stale period boundaries, and invalid/duplicate dates or NAVs.


## SQL/Python reconciliation

No daily-risk metric was calculated.

## Boundary and calendar policy

Monthly SQL returns compound successive observed NAV ratios via a sum of logarithms. Python uses the independent endpoint ratio; interior omissions do not prevent endpoint NAV-change measurement. Each period starts at the last preceding observation and ends at its last observation. No forward-filling occurs. Missing preceding-period boundaries or an unfinished period yield a null period_return, with observed_return retained separately as a partial-window diagnostic. Seven calendar days is a conservative boundary-age screen, not an invented expected valuation calendar. Calendar review/unresolved gap labels remain attached even when the endpoint return is available. No period is labelled calendar-certified complete.

Missing preceding boundaries and unfinished calendar periods are suppressed. Unresolved calendar classifications remain attached. CAGR requires a calendar anniversary and uses elapsed days/365.25. Comparisons use identical actual shared endpoints without ranking equity and bond as peers.

Drawdown is computed only on observed NAVs, with its peak reset at the common-window start. Tied peaks use the latest peak preceding the earliest worst trough. Recovery is the first observed later NAV at or above that peak; duration is calendar days from peak. Unrecovered episodes have null recovery dates/durations and a separately labelled ongoing elapsed duration. Missing NAVs can hide deeper losses or an earlier recovery, so reported observed maximum drawdown is a lower bound on loss magnitude along the unobserved path. It is not a calendar-certified daily-risk statistic.

## Outputs and reproduction

Local Git-ignored outputs: data/processed/performance/summary.csv, monthly_returns.csv, calendar_year_returns.csv, each fund drawdown CSV and combined performance JSON (summary plus all monthly/year records), and validation.json. Source/run lineage remains in daily_nav and the core database. SQL views remain live, so rerun reconciliation after new data.

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m investment_fund_analytics.performance_validation
.\.venv\Scripts\python.exe -m pytest -q
```

## Suppressed and deferred metrics

Six controlled NAV-only risk metrics are implemented separately for the approved restricted window. Sharpe/Sortino and benchmark-relative metrics remain disabled because cash integration/benchmark alignment are incomplete. Calendar and native-NAV adjustment caveats remain. The user completed and manually reviewed five Power BI pages; no direct PBIX inspection by this report is claimed. No ML is implemented. See [publication review](../docs/publication_review.md) for rights and historical-exposure limitations.
