# Separate cash-rate and benchmark validation

Investigated 7 October 2026 after completing the six approved NAV-only risk metrics. No cash-relative or benchmark-relative risk metric was enabled.

## ECB cash-rate feasibility

Official candidate: Euro short-term rate, ISIN EU000A2X2A25, SDMX series **EST.B.EU000A2X2A25.WT**, annual percent (CSV UNIT_MEASURE PC, UNIT_MULT 0). [ECB publication guidance](https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/eurostr_overview.en.html) distinguishes reporting date from next TARGET business-day publication at 08:00 CET; a same-morning correction may occur at 09:00. It states access is free and not licensed by ECB.

Two bounded no-authentication CSV requests succeeded using requests against:

- https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?startPeriod=2023-12-01&endPeriod=2023-12-06&format=csvdata
- https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?startPeriod=2026-09-25&endPeriod=2026-09-30&format=csvdata

The bounded ECB diagnostic requests returned business-date observations near the controlled-window endpoints. Exact sample rates are withheld pending separate reuse/attribution clarification; DWS restrictions are not presumed to govern ECB data. Original responses and pre-redaction notes remain local and Git-ignored. These probes establish endpoint access only, not full-period completeness or cash-return alignment. No cash series was loaded into PostgreSQL. The initial probe stopped on an index HTTP error; later probe logic persists a manifest and HTTP failure status.

Alternative: official compounded cash index **EST.B.EU000A2QQF08.CI**, ISIN EU000A2QQF08. [ECB guidance](https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/eurostr_overview.en.html) describes its backward-looking compounding, publication at 09:15 CET and final values. The bounded index API request returned HTTP 500 in this session; the portal also failed through the browser tool. This is an observed access failure, not proof the series is unavailable. Do not substitute rates or invent index data.

Next cash validation: acquire bounded full rate history with provenance; verify SDMX date semantics/publication timing; use documented ACT/360 accrual across each exact NAV interval, with explicit weekend/TARGET and missing-rate rules; independently reconcile against the official compounded index where accessible. Preserve reference and publication dates and avoid future-rate substitution. Retrospective realized cash return and information available at an investment decision are different concepts. No default zero cash target will be used for Sharpe/Sortino. The implemented zero-target NAV downside statistic remains separate.

## Equity benchmark discrepancy

Rechecked [the official fund page](https://etf.dws.com/en/LU0380865021-euro-stoxx-50-ucits-etf-1c/): it identifies EURO STOXX 50 NTR EUR and month-end reporting boundaries. Private comparison with cached export endpoints found a discrepancy beyond rounding; the month-end rule alone did not explain it. Issuer-displayed returns, export-derived ratios and discrepancy magnitudes are withheld pending redistribution permission. Exact pre-redaction comparisons remain in the verified ignored archive.

Index Level export date convention, actual historical return variant/revisions and provider defects remain candidate explanations, not established facts. No shifting, correlation-based lag selection, replacement or flag clearing was performed. Current official-index identification is supported, but the actual historical exported series needs independent administrator checks at those same four boundaries. If independent official values remain inaccessible, investigate a genuinely matched UCITS proxy with its own fees/calendar limitations; do not present it as the official benchmark or use it to conceal this discrepancy.

The bond export endpoint checks agree with displayed rounded returns, but this does not independently certify all its dates. Both database benchmark candidates remain unverified/flagged, preserving original sources, checksums and effective project assignments. Their four missing levels each also require boundary-aware handling. See [benchmark register](benchmark_sources.md).

Cash full-history acquisition/alignment and benchmark reconciliation remain separate future validation tasks. Sharpe, Sortino, correlation, beta, tracking error and information ratio remain unimplemented.
