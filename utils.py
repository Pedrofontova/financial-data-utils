from datetime import date
import requests
import os

from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """
        Enables retires for requests
        
        Parameters
        ----------
        retries: int
            number of attempts
        backoff_factor: float
            controls the time before making a new request after the first one fails
        status_forcelist: tuple(int)
            the status codes for which a retry is launched
        
        Returns
        -------
        session: requests.session object
            session with retry parameters   
    """
    
    session = requests.Session()
    retry = requests.packages.urllib3.util.retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session


def is_trading_day():
    """
        evaluates if today is a trading day or not
        
        Returns
        -------
        bool
            True if today is a trading day, False if not   
    """
    
    us_business_day = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    
    return date.today() == date.today() + 0 * us_business_day


def get_trading_date_range():
    """
        retrieves the trading days of interest
        
        Returns
        -------
        tuple(str(date))
            tuple containing desired date ranges in string format   
    """
    today_last_year = (date.today() - relativedelta(years=1)).strftime("%Y-%m-%d")
    today = date.today().strftime("%Y-%m-%d")
    tomorrow = (date.today() + relativedelta(days=1)).strftime("%Y-%m-%d")

    return today_last_year, today, tomorrow


def get_pivots(low_list, high_list, n_periods):
    """
        Gets the support(low) and resistance(high) for a given interval 

        Parameters
        ----------
        low_list: list(float)
            a list of floats with the lows of each period
        high_list: list(float)
            a list of floats with the highs of each period

        Returns
        -------
        tuple(tuples)
             a touple with 2 touples, containing lowest and highes levels with number of periods lagging
    """
    
    tmp_low = min(low_list[:n_periods])
    tmp_low_days = low_list[:n_periods].index(tmp_low)
    
    tmp_high = max(high_list[:n_periods])
    tmp_high_days = high_list[:n_periods].index(tmp_high)
    
    return((tmp_low, tmp_low_days), (tmp_high, tmp_high_days))


def get_average_volume(volume_list, n_periods):
    """
        Gets the average volume for a given interval

        Parameters
        ----------
        volume_list: list(float)
            a list of floats with the volume for each period

        Returns
        -------
        float
             the average volume for the given interval
    """
    
    return np.mean(volume_list[:n_periods])


def get_sma_col(df, col_name, window):
    """
        adds moving average column(s) to a dataframe

        Parameters
        ----------
        df: pandas dataframe
            in timeseries format (one row per date), in descending order (older dates at the top)
        col_name: str
            the name of a column contained in the df 
        window: int or list(int)
            the simple moving averages to be calculated (ex. 7, 14)

        Returns
        -------
        new_df: pandas dataframe
            the new df containing all old and new columns 
    """
    
    if isinstance(window, int):
        window = [window]
    
    new_df = df.copy()
    
    for i in window:
        new_df[f'{col_name}_SMA_{str(i)}'] = new_df[col_name].rolling(window=i).mean()
        
    return new_df


def make_candles_df(candles_list):
    """
        Retrieves candle values from a list containing the candles in dictionary format

        Parameters
        ----------
        candles_list: list(dict)
            a list with dictionaries, each containing the candle of a specific period

        Returns
        -------
        pandas DataFrame
            where each row represents a candle in the given timeframe 
    """
    
    values_dict = {
    'start': [], 'end': [], 'open': [], 'close': [], 'low': [], 'high': [], 'volume': [], 'VWAP': []
    }
    
    for i in values_dict.keys():
        for j in range(len(candles_list)):

            values_dict[i].append(candles_list[j][i])

    values_dict['date'] = [pd.to_datetime(tmp).date() for tmp in values_dict['end']]
    values_dict['time'] = [pd.to_datetime(tmp).time() for tmp in values_dict['end']]
            
    return pd.DataFrame(values_dict)


def build_sma_df(sma_dict, sma_days, ticker, gapping_date):
    """
    build a pandas dataframe from a dictionary of dates and SMA values

    Parameters
    ----------
    sma_dict: dict
        dict containing the sma time series in a default range, as returned by alphavantage.get_sma()
    sma_days: str
        number of data points used to calculate each moving average value (ex. '200', '20')
    ticker: str
        the ticker for which to find the sma time series (ex. 'AAPL')
    gapping_date: str
        the current date for which the analysis is run (ex. '2020-03-18')

    Returns
    -------
    df: pandas dataframe
        dataframe containing all info of interest
    """

    dates_list = list(sma_dict.keys())
    ticker_list = [ticker for t in range(len(dates_list))]
    gapping_date_list = [gapping_date for g in range(len(dates_list))]
    sma_vals = [float(tmp['SMA']) for tmp in sma_dict.values()]

    df = pd.DataFrame(
        list(zip(
            ticker_list, 
            dates_list, 
            gapping_date_list, 
            sma_vals)),
        columns = [
            'ticker', 
            'date', 
            'gapping_date', 
            f'SMA_{sma_days}'])

    df = df[df['date'] != gapping_date]

    return df

