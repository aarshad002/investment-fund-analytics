"""Controlled observed-NAV risk; zero-return downside target, no cash/benchmark."""
import numpy as np
import pandas as pd

ANNUALIZATION = 252
MIN_SAMPLE = 252


def interval_series(frame, expected_closures=(), start='2023-12-01', end='2026-09-30'):
    """Classify original consecutive observations without bridging invalid rows."""
    data = frame.copy()
    data['observation_date'] = pd.to_datetime(data.observation_date, errors='raise')
    if data.observation_date.isna().any() or data.observation_date.duplicated().any():
        raise ValueError('Dates must be present and unique')
    if not data.observation_date.is_monotonic_increasing:
        raise ValueError('Dates must be sorted')
    nav = pd.to_numeric(data.nav, errors='coerce').astype(float)
    valid = np.isfinite(nav) & (nav > 0)
    if 'quality_status' in data:
        valid &= data.quality_status.eq('valid')
    data['previous_date'] = data.observation_date.shift()
    data['interval_days'] = (data.observation_date-data.previous_date).dt.days
    data['observed_interval_return'] = nav/nav.shift()-1
    closures = {pd.Timestamp(d).normalize() for d in expected_closures}
    statuses = []
    for i, row in enumerate(data.itertuples()):
        if i == 0:
            status = 'no_prior_observation'
        elif row.previous_date < pd.Timestamp(start) or row.observation_date > pd.Timestamp(end):
            status = 'outside_proposed_risk_window'
        elif not valid.iloc[i] or not valid.iloc[i-1]:
            status = 'flagged_boundary'
        elif any(d.weekday() < 5 and d not in closures for d in
                 pd.date_range(row.previous_date+pd.Timedelta(days=1), row.observation_date-pd.Timedelta(days=1))):
            status = 'unexplained_or_unapproved_weekday_gap'
        else:
            status = 'eligible_if_policy_approved'
        statuses.append(status)
    data['proposed_interval_status'] = statuses
    data['eligible'] = data.proposed_interval_status.eq('eligible_if_policy_approved')
    return data


def summarize(returns, minimum=MIN_SAMPLE):
    """All inputs must already be eligible; preserve count even if suppressed."""
    values = np.asarray(returns, dtype=float)
    if not np.isfinite(values).all() or (values <= -1).any():
        raise ValueError('Finite valid NAV changes required')
    n = len(values)
    result = dict(valid_count=n, status='eligible' if n >= minimum else 'insufficient_history',
                  annualized_volatility=None, downside_deviation=None, var_95=None,
                  expected_shortfall_95=None, tail_count=None)
    if n < minimum:
        return result
    cutoff = np.quantile(values, .05, method='linear')
    tail = values[values <= cutoff]
    result.update(annualized_volatility=float(np.std(values, ddof=1)*np.sqrt(ANNUALIZATION)),
                  downside_deviation=float(np.sqrt(np.mean(np.minimum(values, 0)**2)*ANNUALIZATION)),
                  var_95=float(-cutoff), expected_shortfall_95=float(-tail.mean()), tail_count=len(tail))
    return result


def rolling(intervals, window):
    """Keep original intervals; an excluded interval invalidates the whole window."""
    if window not in (63, 252):
        raise ValueError('Only approved 63/252 observation windows')
    values = intervals.observed_interval_return.where(intervals.eligible)
    counts = values.rolling(window, min_periods=1).count().fillna(0).astype(int)
    volatility = values.rolling(window, min_periods=window).std(ddof=1)*np.sqrt(ANNUALIZATION)
    return pd.DataFrame(dict(observation_date=intervals.observation_date,
                             valid_count=counts, volatility=volatility))
