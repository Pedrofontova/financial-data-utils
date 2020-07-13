
class alphavantage:
    """
        AplaVantage class to make simple requests to AlphaVantage API

        Parameters
        -------
        api_key
            key retrieved from AlphaVantage portal to authenticate the client request
    """
    
    def __init__(self, api_key):
        
        self.api_key = api_key
        self.session = requests_retry_session()
        
    def get_sma(self, ticker, interval, time_period, series_type):
        """
        Get simple moving average for a given ticker
        as described on https://www.alphavantage.co/documentation/#dailyadj
        
        Parameters
        ----------
        ticker: str
            the ticker for which to find the sma time series (ex. 'AAPL')
        interval: str
            time interval between two consecutive data points in the time series(ex. '1min', 'daily')
        time_period: str
            number of data points used to calculate each moving average value (ex. '200', '20')
        series_type: str
            the desired price type in the time series (ex. 'open', 'close')
        
        Returns
        -------
        resp: dict
            dict containing the sma time series in a default range
        """
        
        serv_url = 'https://www.alphavantage.co/query?'
        endpoint = 'function=SMA'
        
        resp = self.session.get(
            serv_url
            + endpoint
            + f'&symbol={ticker}&interval={interval}&time_period={time_period}&series_type={series_type}&apikey={self.api_key}'
        ).json()
        
        return resp['Technical Analysis: SMA']
    

