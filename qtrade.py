
from utils import requests_retry_session
import os

class Questrade:
    """
        Questrade class to authenticate API calls and retrive basic stock information

        Parameters
        -------
        client_token
            token retrieved from Questrade portal to authenticate the client application
    """
    
    
    def __init__(self, client_token):
        
        self.client_token = client_token
        self.session = requests_retry_session()
        self.headers = None
        self.accounts = None
        
        self.get_access_token()
        self.get_accounts()

        
    def get_access_token(self):
        """
            Calls the Qtrade server using a client token, to obtain an api access token

            Returns
            -------
            dict
                a dictionary with the access_token data needed to retrieve information

        """
        
        serv_url = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
        resp = self.session.get(serv_url + self.client_token)

        if resp.text == 'Bad Request':
            raise ValueError('Invalid client token')

        else:
            self.access_token = resp.json()
        
        self.headers = {
            "Authorization": self.access_token["token_type"]
            + " "
            + self.access_token["access_token"]
        }

        self.session.headers.update(self.headers)
        
        return self.access_token
    
    
    def refresh_access_token(self):
        """
            Gets a new access_token using the refresh_token

            Returns
            -------
            dict
                a dictionary with the new access_token data needed to retrieve information

        """
        
        serv_url = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token='
        old_access_token = self.access_token
        resp = self.session.get(serv_url + old_access_token['refresh_token'])

        if resp.text == 'Bad Request':
            raise ValueError('Invalid client token')

        else:
            self.access_token = resp.json()
        
        self.headers = {
            "Authorization": self.access_token["token_type"]
            + " "
            + self.access_token["access_token"]
        }

        self.session.headers.update(self.headers)
        
        return self.access_token

    
    def get_accounts(self, api_version='v1/'):
        """
            Retrieves account information from Qtrade API

            Parameters
            ----------
            api_version: str, default = 'v1/'
                the api version to be used

            Returns
            -------
            dict
                a dictionary containing the different Qtrade accounts for the client
        """
        
        acc_endpoint = 'accounts'

        resp = self.session.get(
            os.path.join(
                self.access_token['api_server'],
                api_version, 
                acc_endpoint
            )
        ).json()
        
        self.accounts = resp

        return self.accounts

    
    def get_candles(self, symbol_id, start_time, end_time, time_interval, api_version='v1/'):
        """
            Retrieves candles of a specific symbol_id, for a specific interval 

            Parameters
            ----------
            symbol_id: str(int)
                a string representing the id integer of the stock (ex. '8049')
            start_time: str(date)
                beginning of interval in 'yyyy-mm-dd' (ex. '2020-03-24')
            end_time: str(date)
                end of interval in 'yyyy-mm-dd' (ex. '2020-03-24')
            time_interval: str
                interval step as defined in url below (ex. OneMinute, OneHour)
                https://www.questrade.com/api/documentation/rest-operations/enumerations/enumerations#historical-data-granularity
            api_version: str, default = 'v1/'
                the api version to be used

            Returns
            -------
            candles: dict
                a dictionary containing the different candles retrieved
        """

        candle_endpoint = 'markets/candles'
        
        start_t = start_time + 'T00:00:00-05:00'
        end_t = end_time + 'T00:00:00-05:00'

        candles = self.session.get(
            os.path.join(
                self.access_token['api_server'], 
                api_version, 
                candle_endpoint
            ) 
            + f'/{symbol_id}?startTime={start_t}&endTime={end_t}&interval={time_interval}'
        ).json()

        return candles
    
    
    def get_quote(self, symbol_id, api_version='v1/'):
        """
            Retrieves stock quotes 

            Parameters
            ----------
            symbol_id: str(int)
                a string representing the id integer of the stock (ex. '8049')
            api_version: str, default = 'v1/'
                the api version to be used

            Returns
            -------
            quote: dict
                a dictionary containing the stock quote information
        """
        
        quotes_endpoint = 'markets/quotes'

        quote = self.session.get(
            os.path.join(
                self.access_token['api_server'], 
                api_version, 
                quotes_endpoint
            )
            + f'/{symbol_id}'
        ).json()

        return quote
    
    
    def get_symbol_id(self, ticker, api_version='v1/'):
        """
            Retrieves symbol ID of a specific ticker

            Parameters
            ----------
            ticker: str
                well known stock ticker (ex. 'AAPL')
            api_version: str, default = 'v1/'
                the api version to be used

            Returns
            -------
            symbol_id: str(int)
                a string representing the id integer of the stock (ex. '8049')
        """
        
        symbol_search_endpoint = 'symbols/search'

        resp = self.session.get(
        os.path.join(
            self.access_token['api_server'], 
            api_version, 
            symbol_search_endpoint
        )
        + f'?prefix={ticker}'
        ).json()

        # search can return more than 1 symbol. We want to return an exact match
        if resp['symbols'][0]['symbol'] == ticker:
            symbol_id = str(resp['symbols'][0]['symbolId'])

        else:
            raise ValueError('No exact match was found for the requested ticker')

        return symbol_id
