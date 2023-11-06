from api_keys import Tokens

from tinkoff.invest import Client, MoneyValue
from tinkoff.invest.services import SandboxService, Services, InstrumentsService, MarketDataService

import pandas as pd
from pandas import DataFrame

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

"""
Для видео по Песочнице https://tinkoff.github.io/investAPI/head-sandbox/
Все видео по API v2 Тинькофф Инвестиции https://www.youtube.com/watch?v=QvPZT5uCU4c&list=PLWVnIRD69wY6j5QvOSU2K_I3NSLnFYiZY

https://tinkoff.github.io/investAPI
https://github.com/Tinkoff/invest-python
"""

def cast_money(v):
    return v.units + v.nano / 1e9

def run():
    print("Песочница API v2 Тинькофф Инвестиции")

    with Client(token=Tokens.api_sandbox_tinkoff) as cl:
        market_data: MarketDataService = cl.market_data

        sb : SandboxService = cl.sandbox
        # print(cl)
        account_id = Tokens.account_sandbox_id
        
        # price = market_data.get_last_prices(figi=["BBG004730ZJ9"])
        # print(cast_money(price.last_prices[0].price))

        # sb.sandbox_pay_in(
        #     account_id=account_id,
        #     amount=MoneyValue(units=100000, nano=0, currency='rub')
        # )

        # АКЦИИ В ПОРТФЕЛЕ
        
        r = sb.get_sandbox_portfolio(account_id=account_id)
        for i in r.positions:
            if i.instrument_type == 'share':
                print(f"figi: {i.figi}, quantity: {i.quantity.units}, average_postions_price: {cast_money(i.average_position_price)}, current price: {cast_money(i.current_price)}\n")
            
        sb.close_sandbox_account(account_id=account_id)

        # r = sb.open_sandbox_account().account_id
        # print(r)

        # r = sb.get_sandbox_accounts().accounts
        # [print(acc.id, acc.opened_date) for acc in r]



def get_portfolio(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService() = cl.sandbox
            account_id = Tokens.account_sandbox_id  # Замените на свой ID аккаунта песочницы
            r = sb.get_sandbox_portfolio(account_id=account_id)
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
        return r

if __name__ == '__main__':
    print(get_portfolio)
    run()