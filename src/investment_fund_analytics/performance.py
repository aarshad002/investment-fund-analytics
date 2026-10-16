"""Endpoint NAV changes and observed-path drawdowns, without daily risk assumptions."""
import pandas as pd
import numpy as np


def series(frame):
    result = frame.copy()
    result['observation_date'] = pd.to_datetime(result.observation_date, errors='raise')
    result['nav'] = pd.to_numeric(result.nav, errors='raise').astype(float)
    if result.empty or result.observation_date.isna().any() or result.observation_date.duplicated().any():
        raise ValueError('Require nonempty, unique, valid observation dates')
    if not np.isfinite(result.nav).all() or (result.nav<=0).any():
        raise ValueError('Require finite positive NAV')
    if 'quality_status' in result and (result.quality_status!='valid').any():
        raise ValueError('Flagged observations require review before performance calculations')
    return result.sort_values('observation_date').reset_index(drop=True)


def calculate(frame):
    frame = series(frame)
    dates, values = frame.observation_date,frame.nav
    start,end = dates.iloc[0],dates.iloc[-1]
    cumulative = values.iloc[-1]/values.iloc[0]-1
    cagr = (1+cumulative)**(365.25/(end-start).days)-1 if end>=start+pd.DateOffset(years=1) else None
    dd = values/values.cummax()-1
    trough = int(dd.idxmin())
    worst = float(dd.iloc[trough])
    peak_date=trough_date=recovery_date=duration=ongoing=None
    status='not_applicable'
    if worst<0:
        peak_value=values.iloc[:trough+1].max()
        peak=int(values.iloc[:trough].loc[lambda s:s==peak_value].index[-1])
        peak_date,trough_date=dates.iloc[peak],dates.iloc[trough]
        recovered=frame.loc[(dates>trough_date)&(values>=peak_value)]
        if recovered.empty:
            status='ongoing'; ongoing=(end-peak_date).days
        else:
            status='recovered'; recovery_date=recovered.observation_date.iloc[0]; duration=(recovery_date-peak_date).days
    return dict(start_date=start,end_date=end,observations=len(frame),cumulative_return=cumulative,cagr=cagr,
                max_drawdown=worst,peak_date=peak_date,trough_date=trough_date,recovery_date=recovery_date,
                recovery_status=status,recovery_duration_days=duration,ongoing_duration_days=ongoing), frame.assign(drawdown=dd)


def period_returns(frame, frequency, gaps=()):
    frame=series(frame)
    if frequency not in {'month','year'}:
        raise ValueError('Choose month or year')
    period_code='M' if frequency=='month' else 'Y'
    periods=frame.observation_date.dt.to_period(period_code)
    records=[]
    for period, group in frame.groupby(periods):
        first=int(group.index[0]); last=int(group.index[-1])
        boundary=frame.iloc[first-1] if first else None
        start=period.start_time.normalize(); end=period.end_time.normalize()
        status='observed_boundaries'
        if boundary is None or boundary.observation_date.to_period(period_code)<period-1 or frame.observation_date.iloc[-1]<end:
            status='partial_period'
        elif (start-boundary.observation_date).days>7 or (end-group.observation_date.iloc[-1]).days>7:
            status='stale_boundary'
        else:
            classifications={g['classification'] for g in gaps
                             if boundary.observation_date<pd.Timestamp(g['gap_date'])<=end}
            if 'unresolved' in classifications: status='unresolved_gap'
            elif 'likely legitimate' in classifications: status='calendar_review'
        observed=float(frame.nav.iloc[last]/(boundary.nav if boundary is not None else group.nav.iloc[0])-1)
        records.append(dict(period_start=start,period_end=end,
                            boundary_date=boundary.observation_date if boundary is not None else None,
                            end_date=group.observation_date.iloc[-1],observations=len(group),status=status,
                            observed_return=observed,
                            period_return=None if status in {'partial_period','stale_boundary'} else observed))
    return pd.DataFrame(records)
