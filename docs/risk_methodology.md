# Controlled observed-NAV methodology — restricted approval

## Current approval record

The user explicitly approved six NAV-only metrics under the calendar/window rules below. Implementation version: approved-controlled-nav-v1-zero-target. Downside deviation uses **zero return**, not cash, as its documented NAV-only target. Cash-relative downside, Sharpe/Sortino and benchmark-relative metrics remain deferred. SQL policy_status is approved_controlled_nav_v1; legacy proposed_interval_status eligible_if_policy_approved is retained for view compatibility and now identifies eligible inputs under the approved policy. See [actual validation](../reports/risk_analysis_validation.md). The restricted approval applies only to these six NAV-only metrics.

Current implementation: approved-controlled-nav-v1-zero-target. Explicit restricted user approval is recorded; cash/benchmark-relative metrics are not approved. DWS source publication permission remains unresolved and redistribution restricted, including derived artifacts.

## Approved calendar and sampling rule

1. Restrict risk estimation to **1 December 2023–30 September 2026**. The unresolved the unresolved historical omission and uncertain old-calendar transition remain in the original histories, but their intervals are outside this approved risk window. The equity historical amendment date remains a caveat; its current explicit exclusion list and observed post-change dates support the operational rule, rather than proving every historical amendment.
2. Use returns between consecutive observed NAVs, retaining both boundary dates and elapsed calendar days. Both boundaries must fall in the risk window and have valid, positive NAVs. Never forward-fill prices, insert zero returns, shift dates or delete source records.
3. Ordinary weekends and reviewed issuer-confirmed excluded weekdays are retained as one **valuation-interval** return, including elapsed-day metadata. Such observations are not asserted to represent equal one-calendar-day horizons. The 252-interval/year convention is an approximation. Historical VaR/ES must be labelled a loss per eligible NAV valuation interval, not a guaranteed one-calendar-day loss threshold.
4. Exclude an interval containing any other absent weekday: likely legitimate, unresolved or absent from the reviewed calendar register. Preserve the excluded interval with its reason; do not join across it. Pre-window intervals are excluded from risk inputs while remaining available for existing performance outputs.
5. Retain actual row ordering when constructing rolling windows; require every one of the latest 63 or 252 consecutive interval rows to be eligible. Do not simply drop rejected rows and roll over the compressed series. Require at least 252 eligible observations for full-window risk metrics, and at least 63 for 63-interval rolling volatility.
6. Benchmark-relative calculations require both identical previous/current boundary dates and a benchmark whose identity, basis, effective assignment and date alignment are cleared. Current loaded benchmark series are flagged, so correlation, beta, tracking error and information ratio remain blocked independently of calendar approval.

All are visible in analytics.nav_intervals. Its policy_status is approved_controlled_nav_v1; approved NAV-only summary/rolling results are exposed separately.

## Cash target and formulas for later approval

Sharpe, cash-relative downside deviation and Sortino require matched EUR cash returns derived from official ECB €STR, not zero by default. Acquire/document rate reference dates, publication dates, quoted annual percentages and ACT/360 convention. For an observed interval, compound applicable cash factors across calendar days; use the documented rate for its reference period, handle weekends/holidays explicitly and do not substitute future rates. Historical realized cash comparisons are descriptive, not a predictive strategy; publication information must still be preserved. Only small cash feasibility samples exist; full cash history is not integrated, so cash-relative metrics remain suppressed. Implemented NAV-only downside deviation uses zero return and is distinct.

Implemented sample valuation-interval standard deviations use ddof=1 and sqrt(252) annualization. Sharpe uses mean excess return/sample SD of excess return × sqrt(252). The deferred cash-relative downside deviation is sqrt(mean(min(excess,0)^2)) × sqrt(252), averaging over all eligible cash-aligned observations; Sortino is 252 × mean excess return divided by annualized downside deviation. Denominator zero means null.

Historical 95% VaR is minus the linear-interpolated 5th percentile of eligible returns. Expected shortfall is minus the mean of returns at/below that cutoff, retaining ties and tail counts. Beta is sample covariance divided by benchmark variance; correlation is Pearson correlation. Tracking error is sample SD of active returns × sqrt(252); information ratio is mean active return/sample SD active return × sqrt(252). Use identical paired samples, preserve counts, and suppress insufficient history/zero denominators. No return clipping, causal claims or regulatory risk ratings.

## Approval record

**Restricted approval recorded.** Six NAV-only metrics are implemented for the fixed window. Sharpe/Sortino, correlation, beta, tracking error and information ratio remain disabled. Publication rights, benchmark alignment and cash eligibility are independent gates, not waived by calendar approval.
