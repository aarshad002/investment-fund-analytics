# Calendar completeness review

## Approved operational restriction — 7 October 2026

The user approved controlled NAV-only risk for 2023-12-01–2026-09-30. Weekends/reviewed issuer closures are retained with elapsed days; other missing weekdays exclude the spanning interval. No filling occurs. SQL policy_status is approved_controlled_nav_v1. Earlier pending-approval statements below are historical. See [risk validation](risk_analysis_validation.md).

## Controlled-risk stage update — explicit approval pending

Further issuer-document review has not resolved the unresolved historical omission or established the exact historical equity calendar amendment date. No omission has been reclassified merely to enable calculations.

The concrete [controlled-risk proposal](../docs/risk_methodology.md) uses 1 December 2023–30 September 2026 only. Returns use consecutive observed NAV dates and retain elapsed calendar days. Ordinary weekends and reviewed issuer exclusions are retained as valuation intervals; intervals spanning any other absent weekday are excluded. No NAV is forward-filled and no missing observation becomes a zero return. Rolling windows must not bridge excluded intervals.

This operational restriction is not a resolution of the full five-year calendar. The 252-interval annualization assumption and variable calendar-day horizons must be disclosed. Historical tail losses would be labelled per eligible valuation interval. **Daily-risk calculations remain deferred until the user explicitly approves the proposed methodology.** Benchmark alignment and cash-series validation are separate gates.

Reviewed 7 October 2026. This report supersedes the unclassified weekday screen in the full-history report. No NAV dates or values have been invented, filled, shifted, or deleted.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

## Evidence and interpretation

Evidence codes used in the register:

- **OLD**: the issuer's [April 2022 Xtrackers prospectus hosted by HKEX](https://www1.hkexnews.hk/listedco/listconews/sehk/2022/0429/2022042901891.pdf), printed pages 1, 5–6 and 10, connects NAV dates to business days requiring both Luxembourg and London banking days; banking half-days are excluded. It supports the old-calendar interpretation but does not prove every effective-date/product exception for these two classes.
- **NEW**: [Xtrackers II notice dated 17 November 2023](https://etf.dws.com/download/asset/77e675e1-a38e-4535-9517-2578db5a0475), pages 1–2, changes NAV-date exclusions effective 1 December 2023. The [current Xtrackers prospectus](https://etf.dws.com/download/asset/97f28cea-2f24-445d-b135-f9c31a5f884d), printed pages 18 and 22, has matching general exclusions; its Euro Stoxx 50 annex is on printed pages 125–126. These support expected post-change omissions. The exact historical effective date for the equity umbrella has not been independently established: its post-change classification is consistent with its current rule, not a certification of its historical calendar.
- **LU**: [Luxembourg government holiday guidance](https://guichet.public.lu/en/citoyens/travail/conges-jours-feries/jours-feries/travail-jours-feries.html) identifies statutory holidays and banking Good Friday/Christmas Eve afternoon. Easter-related dates were matched to the historical calendar. Public holidays alone do not establish fund NAV exclusions.
- **UK**: [GOV.UK historical England and Wales bank holidays](https://www.gov.uk/bank-holidays) provides dated 2021–2023 schedules, including substitutes, Jubilee, funeral and coronation holidays. London operations matter even though both funds are Luxembourg-domiciled.
- **TARGET**: [ECB long-term TARGET closing calendar](https://www.ecb.europa.eu/press/pr/date/2000/html/pr001214_4.en.html) provides the recurring closure rules. This is a payment-system calendar, not a complete fund or exchange calendar.
- **EXCHANGE**: [Euronext historical trading schedules](https://www.euronext.com/en/trading/trading-hours-holidays), 2022 table, identifies a Dublin half-day on 23 December. Other listed venues had full sessions. This does **not** prove that either selected fund should lack a NAV.

The issuer distinguishes the NAV date (date valued) from the later valuation day (calculation/publication). The workbook Date is retained as reported; no publication-date lag adjustment is applied. No fund-specific suspension or publication notice has been located for the unresolved historical omission. It remains unexplained at issuer level, rather than being labelled a legitimate publication gap.

## Observed omission records withheld

E = expected/non-valuation day; L = likely legitimate; U = unresolved. L identifies credible holiday evidence while preserving uncertainty about historical product calendars.

Detailed observation-derived table withheld pending permission; exact evidence is retained locally.

## Completeness and daily-analysis decision

**Unrestricted five-year daily analysis remains uncertified.** Controlled risk uses the separately approved window and consecutive observed NAVs. Preserve interval lengths, exclude intervals spanning unapproved omissions and never fill NAVs or manufacture zero returns. Public holiday rules alone cannot certify a fund valuation calendar. Detailed observed omissions and evidence outcomes are withheld locally.

The populated register is at data/interim/calendar/calendar_gap_register.csv; the public CSV is a header-only schema template. Reconstruct from authorized local quality evidence, then review before loading. Existing preserved records are never overwritten by reconstruction. See [reproduction guide](../docs/reproduction_guide.md).

Remaining calendar actions: locate class-specific historical calendar amendments/holiday notices, especially the transition during 2023 and the unresolved historical omission, or obtain issuer clarification. No message was sent to the issuer. Calendar checking can be reproduced offline with `python -m investment_fund_analytics.calendar_validation` after setting `PYTHONPATH=src`; it classifies only already-observed omissions and defaults unfamiliar dates to unresolved.
