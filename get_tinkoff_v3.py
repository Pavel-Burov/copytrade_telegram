from datetime import datetime
from api_keys import Tokens
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, Quotation, InstrumentIdType
from tinkoff.invest.services import InstrumentsService, MarketDataService
from pandas import DataFrame
import math
import pandas as pd
from tinkoff.invest.services import SandboxService



def cast_money(v):
    return v.units + v.nano / 1e9

def get_available_money(sandbox_mode=True):
    # return int
    pass

def get_positions():
    # https://russianinvestments.github.io/investAPI/operations/#portfolioposition
    # return dict {ticker:percent}
    pass

def get_shares_data(ticker):
    # return figi, lot, last_price
    pass

def sell_all():
    pass

def buy():
    pass

def sell():
    pass

def process_orders(order_dict):
    if get_positions() == order_dict:
        pass
    