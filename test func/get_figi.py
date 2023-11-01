from pandas import DataFrame
from tinkoff.invest import Client, InstrumentStatus, SharesResponse, InstrumentIdType
from tinkoff.invest.services import InstrumentsService, MarketDataService


from api_keys import Tokens

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

TICKER = "ALRS"

def cast_money(v):
    return v.units + v.nano / 1e9

def get_figi(Ticker):
    with Client(Tokens.api_main_tinkoff) as cl:
        instruments: InstrumentsService = cl.instruments
        # market_data: MarketDataService = cl.market_data

        # r = instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id="BBG004S683W7")
        # print(r)
        # print(
        #     r.instrument.figi,
        #     r.instrument.ticker,
        #     r.instrument.min_price_increment,
        #     H.cast_money(r.instrument.min_price_increment)
        # )

        l = []
        for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
            for item in getattr(instruments, method)().instruments:
                l.append({
                    'ticker': item.ticker,
                    'figi': item.figi,
                    'type': method,
                    'name': item.name,
                    'min_inc_o': item.min_price_increment,
                    'min_inc': cast_money(item.min_price_increment)
                })

        df = DataFrame(l)
        # df.to_json()
        print(df.tail(1))

        df = df[df['ticker'] == Ticker]
        if df.empty:
            print(f"Нет тикера {Ticker}")
            return
        
        # print(df.iloc[0])
        result_figi = df['figi'].iloc[0]
        return result_figi


if __name__ == '__main__':
    get_figi(TICKER)