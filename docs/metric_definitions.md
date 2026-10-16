# Metric definitions

## Approved controlled NAV-only risk

Version approved-controlled-nav-v1-zero-target implements six metrics: sample volatility, **zero-target** downside deviation, linear historical 95% VaR, tied-cutoff expected shortfall and 63/252-observation rolling sample volatility. Volatility/downside use sqrt(252). Zero target is distinct from the deferred cash-target definitions. Preserve elapsed days; retain weekends/reviewed issuer closures; exclude unexplained weekdays; never fill NAVs or compress rolling gaps. Summary minimum count is 252; rolling requires all 63/252 consecutive rows eligible. VaR/ES refer to valuation intervals with varying calendar horizons. See [risk validation](../reports/risk_analysis_validation.md). Cash/benchmark-relative metrics remain disabled; unrestricted five-year daily-risk analysis is not cleared.

## Phase 4 implemented scope — phase4-observed-nav-v1

The approved Phase 4 subset now implements endpoint native-NAV changes, CAGR, monthly/year periods and **observed-path** drawdowns. The result is explicitly restricted to the observed path, can miss an unobserved deeper trough/earlier recovery, and is not a certified full-calendar daily-risk result. It does not imply that native NAV is a separately verified corporate-action-adjusted total-return index.

Period boundaries use the last observed prior-period NAV and last observed within-period NAV. No missing NAV is filled. A missing preceding-period boundary, unfinished calendar period or boundary age beyond seven calendar days suppresses the full-period return; an observed partial-window change remains separately labelled. Seven days is a conservative staleness rule, not an assertion about expected valuation dates. `unresolved_gap` and `calendar_review` statuses preserve interior-calendar caveats even when endpoint returns are available. `observed_boundaries` means those operational boundary checks passed, not that the fund calendar is certified.

CAGR requires at least a calendar anniversary; actual years equal elapsed days/365.25. The comparison starts/ends on dates actually shared by the approved funds. Maximum drawdown uses the latest tied peak before the earliest worst trough, first observed post-trough recovery at or above peak, and calendar-day peak-to-recovery duration. No-loss paths have `not_applicable` recovery; unrecovered paths retain null recovery dates/duration and a separate ongoing duration through the as-of date.

SQL views are in [performance_views.sql](../sql/performance_views.sql); Python definitions are in `src/investment_fund_analytics/performance.py`. See [live reconciliation report](../reports/performance_analysis_validation.md). The six approved controlled NAV-only risk metrics are implemented separately; cash/benchmark-relative metrics remain deferred. Shared conventions below describe current semantics and genuinely deferred formulas.

Specification consolidated 16 October 2026. Performance and restricted NAV-only risk calculations are implemented; cash/benchmark-relative formulas below are specifications only, not enabled outputs. Read alongside the [data dictionary](data_dictionary.md) and [project plan](project_plan.md).

## Eligibility and shared conventions

Use verified valuation-date series, ascending and unique. Initial instruments are the EUR accumulating NAV classes LU0380865021 and LU0290355717. Their native NAV is not yet a verified split-adjusted total-return series. Corporate-action checks must precede financial interpretation. Distributing classes require a documented reinvested-distribution series; otherwise label NAV/price change and suppress total-return comparisons.

Let V(t) be an eligible positive wealth-equivalent value, r(t) a simple return, c(t) the cash return over the same interval, b(t) the benchmark return, and e(t)=r(t)-c(t). Store returns as decimals; display percentages. Ratios are unitless. Use sample standard deviation/covariance (`ddof=1`), A=252 for daily annualization, and elapsed years = calendar days/365.25 for CAGR. These are conventions, not guarantees of statistical independence.

Daily risk inputs require consecutive expected valuation observations under the instrument's documented calendar. Friday-to-Monday is a normal interval; a missing expected valuation is a gap. Do not call a multi-observation-gap return a daily return, fill missing prices, or manufacture zero returns. Calendar coverage and gap classification must be explicit. Flagged observations are excluded pending resolution; do not bridge excluded points into daily risk inputs. Period returns may use validated boundary NAVs despite interior gaps, with path warnings. Observed-path drawdowns retain the documented incomplete-path caveat. Daily-risk inputs use the approved restricted window and eligibility rule; they do not certify the full historical calendar.

Metrics carry instrument, basis, currency, as-of date, actual boundaries, window, valid count, methodology version and eligibility status. Undefined results are null with a reason. At least 252 eligible daily returns are required for full-window annualized volatility, ratios, beta, correlation and historical tail metrics. Rolling 63-observation volatility is an explicitly labelled exception: require all 63 eligible returns; 252-observation rolling metrics require all 252. Five-year comparisons require five elapsed years and 60 complete monthly return intervals. A one-day-old boundary valuation outside the displayed range may be required for the first return.

Use the final valid valuation on or before each requested calendar boundary, and record the actual dates. Stale boundaries beyond the documented calendar allowance suppress the result. YTD starts at the final prior-year valuation. Never mix native and EUR-converted series or a hedged fund with an unmatched unhedged benchmark.

## Performance KPIs

| Metric | Formula / definition | Window and output |
| --- | --- | --- |
| Simple return | r(t)=V(t)/V(t-1)-1 | Observation interval; label gap-spanning returns separately |
| Cumulative return | product(1+r(t))-1; equivalently ending/start wealth minus 1 for a valid consistent path | Decimal; boundary values must be eligible |
| Rebased wealth | 100 × V(t)/V(start) | Starts at 100; use actual displayed starting valuation |
| CAGR | (V(end)/V(start))^(1/elapsed_years)-1 | Minimum one elapsed year; suppress shorter-window annualization |
| YTD / trailing 1, 3, 5-year return | Compound over explicit boundary intervals | 1-year cumulative; multi-year cards explicitly labelled cumulative or annualized |
| Monthly/calendar-year return | Ending wealth/prior-period-end wealth minus 1 | A complete period needs a valid preceding boundary; incomplete current periods labelled separately |
| Benchmark excess return | Fund cumulative return minus benchmark cumulative return | Percentage-point difference over identical boundaries |
| Positive-month proportion | Count of complete valid months with return >0 / count of complete valid months | Zero months are not positive; denominator displayed |
| Ongoing charges | Issuer figure at documented effective date | Descriptive context; no second fee deduction from net NAV |
| Data coverage | Observed valid valuations / expected valuations | Instrument-specific calendar and raw counts; daily-risk return coverage separate |

EUR conversion: where q(t) is foreign-currency units per EUR, V_EUR(t)=V_foreign(t)/q(t). Use only FX observations available on/before valuation date with a declared maximum age. EUR reporting does not turn an unhedged fund into a hedged class. No FX implementation is included in Phase 1.

## Risk and relative-performance metrics

| Metric | Formula / definition | Interpretation and eligibility |
| --- | --- | --- |
| Annualized volatility | sd(r) × sqrt(A) | Historical daily dispersion; sample standard deviation |
| Drawdown | W(t)/max(W(s), s<=t)-1 | Nonpositive fraction; W is consistent wealth series |
| Maximum drawdown | min(drawdown) | Negative percentage; report peak and trough dates |
| Recovery duration | Calendar days from drawdown peak to first subsequent W>=peak wealth | Report ongoing/unrecovered separately, plus elapsed days at as-of date |
| Annualized zero-target downside deviation (implemented) | sqrt(mean(min(r(t),0)^2)) x sqrt(A) | Mean over all eligible NAV intervals; zero target, no cash series required |
| Annualized cash-target downside deviation (deferred) | sqrt(mean(min(e(t),0)^2)) × sqrt(A) | Mean includes all eligible intervals, including zero downside contributions |
| Sharpe ratio | mean(e)/sd(e) × sqrt(A) | Suppress zero denominator; matching cash intervals required |
| Sortino ratio | A × mean(e) / annualized downside deviation | Same cash target; suppress zero downside denominator |
| Historical 95% VaR | -quantile(r,0.05) | Eligible valuation-interval loss threshold with variable calendar-day horizons; linear quantile interpolation; signed result, no clipping at zero |
| Historical 95% expected shortfall | -mean(r where r<=quantile(r,0.05)) | Includes all ties at threshold; disclose tail count and sample size |
| Tracking error | sd(r-b) × sqrt(A) | Aligned daily fund/benchmark intervals and matching currency/basis |
| Information ratio | mean(r-b)/sd(r-b) × sqrt(A) | Zero active-return dispersion produces null |
| Beta | sample_cov(r,b)/sample_var(b) | Null for zero benchmark variance; neither causal nor guaranteed exposure |
| Correlation | sample_cov(r,b)/(sd(r)×sd(b)) | Null for either zero variance; return-series comparison |
| Rolling volatility / Sharpe | Same formulas on the latest 63/252 eligible consecutive daily intervals | Full calendar-validated window only; Sharpe uses 252 intervals |

Cash proxy: use EUR €STR, aligned to each actual elapsed calendar-day return interval. Convert annual quoted percentages to decimals and accrue using ACT/360: compound the eligible daily cash factors `(1 + annual_rate × applicable_days/360)`. Account for weekends/holidays and publication timing; no lookahead. Rate carry-forward requires a stated maximum age and failure status. XEON is not the cash-rate series. Only small ECB access samples exist; full cash history/alignment is not integrated, so Sharpe/Sortino remain deferred. Implemented NAV-only downside targets zero return; cash-target downside remains a separate deferred specification.

Benchmarks need explicit identity, currency, return variant and effective assignment dates. Bundled DWS Index Level data does not automatically establish permission or compatible adjustment conventions. Proxy ETF comparisons must say proxy and disclose fees/tracking differences. No benchmark-dependent result is eligible until those checks pass.

Maximum drawdown conventions: running peak includes the current observation. Tied peaks use the latest peak before descent; equal worst troughs use the earliest trough. Recovery begins after the trough and is measured from the associated peak. For a path with no drawdown, maximum drawdown is zero and recovery is not applicable. Window-relative drawdown resets its peak at window start and must be labelled accordingly; an all-history underwater chart preserves earlier peaks. Do not mix those definitions.

Historical VaR/ES do not forecast all future losses and are not regulatory risk measures. Stress periods must be declared before reviewing rankings, remain inside observed history, and use the same method as ordinary windows. Comparisons/rankings require compatible categories and common dates; the equity and bond test pair is a source test, not a peer ranking.

## Planned calculation verification

Future tests should cover a constant-value series (zero volatility and undefined Sharpe), known compounded returns, a peak/trough/recovery sequence, unrecovered drawdown, tied quantiles, missing expected valuations, zero benchmark variance, invalid/nonpositive values, date boundaries, EUR quote direction and fee double-counting. Independently reconcile selected SQL and Python calculations within absolute tolerance 1e-10 for returns/ratios or a documented looser source-rounding tolerance. Store precision must be reviewed before assuming that tolerance for all data.

Native NAV adjustment semantics, cash-rate availability/publication alignment, exact fund calendars, benchmark permissions and corporate actions remain implementation prerequisites. This specification fixes formulas and missing-value behavior; it does not imply those prerequisites have passed.
