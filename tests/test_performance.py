import pandas as pd
import pytest
from investment_fund_analytics.performance import calculate,period_returns


def nav(dates,values):
    return pd.DataFrame({'observation_date':dates,'nav':values})


def test_known_compounded_sequence():
    result,_=calculate(nav(['2023-01-01','2023-01-02','2023-01-03'],[100,110,99]))
    assert result['cumulative_return']==pytest.approx(-.01)
    assert result['cagr'] is None


def test_constant_series_has_no_drawdown_or_recovery():
    result,path=calculate(nav(['2023-01-01','2024-01-01'],[100,100]))
    assert result['cumulative_return']==result['cagr']==result['max_drawdown']==0
    assert result['recovery_status']=='not_applicable' and result['peak_date'] is None
    assert (path.drawdown==0).all()


def test_latest_tied_peak_earliest_worst_trough_and_recovery():
    result,_=calculate(nav(pd.date_range('2023-01-01',periods=6),[100,120,120,90,90,120]))
    assert result['max_drawdown']==pytest.approx(-.25)
    assert result['peak_date']==pd.Timestamp('2023-01-03')
    assert result['trough_date']==pd.Timestamp('2023-01-04')
    assert result['recovery_date']==pd.Timestamp('2023-01-06')
    assert result['recovery_duration_days']==3


def test_unrecovered_episode_is_ongoing_not_zero_duration():
    result,_=calculate(nav(['2023-01-01','2023-01-03'],[120,90]))
    assert result['recovery_status']=='ongoing'
    assert result['recovery_duration_days'] is None and result['ongoing_duration_days']==2


def test_incomplete_month_is_suppressed_and_observed_partial_is_separate():
    periods=period_returns(nav(['2023-01-15','2023-01-31','2023-02-10'],[100,110,121]),'month')
    assert list(periods.status)==['partial_period','partial_period']
    assert periods.period_return.isna().all()
    assert list(periods.observed_return)==pytest.approx([.1,.1])


def test_complete_month_uses_previous_month_boundary():
    periods=period_returns(nav(['2022-12-30','2023-01-03','2023-01-31'],[100,105,110]),'month')
    assert periods.iloc[-1].period_return==pytest.approx(.1)


def test_calendar_anniversary_gate_handles_nonleap_and_leap_years():
    result,_=calculate(nav(['2023-01-01','2024-01-01'],[100,110]))
    assert result['cagr']==pytest.approx(1.1**(365.25/365)-1)
    result,_=calculate(nav(['2024-01-01','2025-01-01'],[100,110]))
    assert result['cagr']==pytest.approx(1.1**(365.25/366)-1)
    result,_=calculate(nav(['2023-01-01','2023-12-31'],[100,110]))
    assert result['cagr'] is None


def test_missing_observations_keep_endpoint_return_but_flag_path():
    frame=nav(['2022-11-30','2022-12-22','2022-12-28','2022-12-30','2023-01-03'],[100,110,120,121,122])
    periods=period_returns(frame,'month',[dict(gap_date='2022-12-23',classification='unresolved')])
    december=periods.iloc[1]
    assert december.status=='unresolved_gap' and december.period_return==pytest.approx(.21)
    _,path=calculate(frame)
    assert len(path)==5  # no generated NAV dates or fabricated losses


def test_absent_previous_month_suppresses_period_and_stale_boundary():
    p=period_returns(nav(['2023-01-31','2023-03-31','2023-04-30'],[100,110,120]),'month')
    assert p.iloc[1].status=='partial_period' and pd.isna(p.iloc[1].period_return)
    p=period_returns(nav(['2023-01-20','2023-02-28'],[100,110]),'month')
    assert p.iloc[1].status=='stale_boundary' and pd.isna(p.iloc[1].period_return)


def test_duplicate_nonpositive_and_missing_dates_rejected():
    for dates,values in [(['2023-01-01']*2,[100,101]),(['2023-01-01'],[0]),([None],[100])]:
        with pytest.raises(ValueError):calculate(nav(dates,values))
