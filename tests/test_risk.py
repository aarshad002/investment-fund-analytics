import numpy as np
import pandas as pd
import pytest
from investment_fund_analytics.risk import summarize, interval_series, rolling


def test_known_volatility():
    values=np.tile([-.02,.01,.03,-.01],63)
    assert summarize(values)['annualized_volatility']==pytest.approx(np.std(values,ddof=1)*np.sqrt(252))


def test_zero_target_downside_uses_all_observations():
    values=np.tile([-.02,.01],126)
    assert summarize(values)['downside_deviation']==pytest.approx(np.sqrt(.02**2/2*252))


def test_linear_var():
    values=np.linspace(-.05,.05,252)
    assert summarize(values)['var_95']==pytest.approx(.045)


def test_expected_shortfall_includes_cutoff_ties():
    values=[-.1]*20+[.01]*232
    result=summarize(values)
    assert result['tail_count']==20
    assert result['expected_shortfall_95']==pytest.approx(.1)


@pytest.mark.parametrize('window',[63,252])
def test_rolling_known_sequence_and_excluded_interval(window):
    values=np.resize([-.02,.01],window*3)
    data=pd.DataFrame(dict(observation_date=pd.bdate_range('2024-01-01',periods=len(values)),
                           observed_interval_return=values,eligible=True))
    out=rolling(data,window)
    assert pd.isna(out.volatility.iloc[window-2])
    assert out.volatility.iloc[window-1]==pytest.approx(np.std(values[:window],ddof=1)*np.sqrt(252))
    data.loc[window,'eligible']=False
    out=rolling(data,window)
    assert out.volatility.iloc[window:window*2].isna().all()
    assert out.valid_count.iloc[window*2-1]==window-1
    assert pd.notna(out.volatility.iloc[window*2])


def test_constant_and_positive_only_signed_tail():
    out=summarize([0]*252)
    assert all(out[k]==0 for k in ('annualized_volatility','downside_deviation','var_95','expected_shortfall_95'))
    assert summarize([.01]*252)['var_95']==pytest.approx(-.01)


def test_insufficient_and_invalid():
    assert summarize([.01]*251)['status']=='insufficient_history'
    assert summarize([.01]*251)['annualized_volatility'] is None
    with pytest.raises(ValueError):summarize([np.nan]*252)


def test_calendar_weekend_confirmed_holiday_and_unexplained_gap():
    data=pd.DataFrame(dict(observation_date=['2023-12-01','2023-12-04','2023-12-06','2023-12-08'],nav=[100,101,102,103]))
    result=interval_series(data,expected_closures=['2023-12-05'])
    assert result.eligible.tolist()==[False,True,True,False]
    assert result.interval_days.iloc[1]==3
    assert len(result)==4


def test_flagged_boundary_never_bridged():
    frame=pd.DataFrame(dict(observation_date=pd.bdate_range('2024-01-01',periods=4),nav=[100,101,102,103],
                            quality_status=['valid','flagged','valid','valid']))
    assert interval_series(frame).eligible.tolist()==[False,False,False,True]


def test_fixed_window_end_does_not_expand_with_future_data():
    data=pd.DataFrame(dict(observation_date=['2026-09-29','2026-09-30','2026-10-01'],nav=[100,101,102]))
    assert interval_series(data).eligible.tolist()==[False,True,False]
