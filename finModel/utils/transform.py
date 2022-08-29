'''
Houses all the assumption functions and transformations we are going to use for generating forecasts of the
various financial statements.
'''

import statsmodels.formula.api as smf
from typing import List, Hashable
import pandas as pd
import numpy as np


def add_movement(on:pd.Series,movement:pd.Series) -> pd.Series:
    '''
    Add the current year movement to beginning-of-the-period position and get back the new positions
    :param on: series that contains the beginning position
    :param movement: movements of each period
    :return: closing position
    '''
    last_date_actuals: np.datetime64 = on.index.max()
    start_pos: float = on[last_date_actuals]
    ser_with_start: pd.Series = pd.Series(start_pos).append(movement[movement.index > last_date_actuals])
    return ser_with_start.cumsum()[1:]


def days_outstanding(num:pd.Series,den:pd.Series,f:int=360) -> np.ndarray:
    '''
    Generate the DSO/DIO/DPO metrics as an annualised %
    :param num: trade receivable/payables or inventory
    :param den: revenues
    :param f: days in the period
    '''
    return np.array([f*(num[idx]/den[idx]) for idx in num.index],dtype=float)


def mean_g(ser: pd.Series) -> np.float:
    '''
    Calculate average of period-on-period growth rates when provided with level values.
    '''
    mean = np.nanmean((ser/ser.shift(1))-1)
    return mean


def const_pandas_series(name: Hashable, f_dates: List[str],const:np.ndarray=np.array(0.0)) -> pd.Series:
    '''
    Create a pandas series with 0 values and indexed at f_dates; to be used to populate forecast() under financial
    statements.
    :param name: name to provide
    :param f_dates: index
    :return: zero-valued pandas series
    '''
    return pd.Series(np.repeat(const,len(f_dates)),index=np.array(f_dates,dtype="datetime64"),name=str(name))


def const_growth(ser: pd.Series, g: float, f_dates: List[str]) -> pd.Series:
    '''
    Project the most recent value of the series based on a constant growth rate
    :param ser: series to project
    :param g: growth-rate to use
    :param f_dates: dates to forecast upon
    :return: forecasted values
    '''
    factor: List[float] = [np.power(1+g,1+idx) for idx in np.arange(0,len(f_dates))]
    recent_val: float = ser[np.max(ser.index)]
    forecast: pd.Series = pd.Series(data=[recent_val*f for f in factor],
                                    index=np.array(f_dates,dtype='datetime64'),
                                    name=ser.name)
    return forecast


def const_share(fcast: pd.Series, shr: np.ndarray, f_dates: List[str]) -> pd.Series:
    '''
    Project a series based on a constant share of a already forecasted series
    :param fcast: forecasted series
    :param g: percentage-share
    :param f_dates: dates to forecast upon
    :return: forecasted shares
    '''
    forecast_shr: pd.Series = pd.Series(data=[f*shr for f in fcast],
                                    index=np.array(f_dates,dtype='datetime64'),
                                    name=fcast.name)
    return forecast_shr


def linear_trend(ser: pd.Series, f_dates: List[str]) -> pd.Series:
    '''
    Generate linear model forecasts of the series using OLS linear regression based on historical values provided
    :param ser: series to fit model upon
    :param f_dates: dates to forecast upon
    :return: forecasted values
    '''
    train_df: pd.DataFrame = pd.DataFrame(ser)
    min_date: np.datetime64 = train_df.index.min()
    train_df['days'] = (train_df.index - min_date).days + 1
    test_df: pd.DataFrame = pd.DataFrame({
        ser.name: np.repeat(0.0,len(f_dates)),
        'days': [(np.datetime64(date)-min_date).days + 1 for date in f_dates]
    },index=np.array(f_dates,dtype="datetime64"))
    model = smf.ols(f"{ser.name} ~ days",train_df).fit()
    test_df[ser.name] = model.predict(test_df)
    forecast: pd.Series = test_df[ser.name]

    return forecast