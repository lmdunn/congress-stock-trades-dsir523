import pandas as pd
import requests as req
import sys
import time
sys.path.insert(0, '../../../API_keys')
from vantage_api import alpha_vantage_key
def stock_code(tickers):
    stock_dict = {}
    '''
    for i in tickers:
        json = res.get('https://finance.yahoo.com/quote/' + i + '?p=' + i + '&.tsrc=fin-srch',
                  params = {
                      'function': 'TIME_SERIES_DAILY',
                      'outputsize': 'full',
                      'symbol': ticker,
                      'apikey':av_api_key
                  }).json()
    '''
    return 1 + 1