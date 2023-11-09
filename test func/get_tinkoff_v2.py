from datetime import datetime
from numpy import average

from sympy import true
from api_keys import Tokens
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, Quotation, InstrumentIdType
from tinkoff.invest.services import InstrumentsService, MarketDataService
from pandas import DataFrame
import math, time
import pandas as pd
from tinkoff.invest.services import SandboxService


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def cast_money(v):
    return v.units + v.nano / 1e9


def get_available_money(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            return r.total_amount_currencies.units
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            return r.total_amount_currencies.units

def get_total_capital(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            return cast_money(r.total_amount_portfolio)
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            return cast_money(r.total_amount_portfolio)

def get_shares_data(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            for i in r.positions:
                if i.instrument_type == 'share':
                    return i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)
        else:
            r=cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            for i in r.positions:
                if i.instrument_type == 'share':
                    return i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)


def get_figi(Ticker):
    with Client(Tokens.api_main_tinkoff) as cl:
        instruments: InstrumentsService = cl.instruments
        market_data: MarketDataService = cl.market_data
        l = []
        for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
            for item in getattr(instruments, method)().instruments:
                l.append({
                    'ticker': item.ticker,
                    'figi': item.figi,
                    'type': method,
                    'name': item.name,
                    'lot': item.lot,
                    'min_inc_o': item.min_price_increment,
                    'min_inc': cast_money(item.min_price_increment)
                })

        df = DataFrame(l)

        df = df[df['ticker'] == Ticker]
        if df.empty:
            print(f"Нет тикера {Ticker}")
            return None

        result_lot = df['lot'].iloc[0]
        result_figi = df['figi'].iloc[0]
        price = market_data.get_last_prices(figi=[result_figi])
        last_price = cast_money(price.last_prices[0].price)

        return result_figi, result_lot, last_price
    

class Trade:
    def process_orders(order_dict,  real_positions, sandbox_mode=True):
        print(f"connect Tinkoff: {order_dict}, {real_positions}")
        if real_positions == order_dict:
            print("next")
            return None
        current_positions = real_positions
        try:
            print("Get total capital...")
            total_capital = get_total_capital(sandbox_mode)
            print(f"Total capital: {total_capital}")
            print("successfully")
        except Exception as ex:
            print(f"Error get_total_capital: {ex}")
        for current_ticker, current_percent in real_positions.items(): # НЕ РАБОТАЕТ ИЗ ЗА ТОГО ЧТО ЦИКЛ ИДЕТ ПО ПУСТОМУ СЛОВАРЮ
            for ticker, percent in order_dict.items():
                percent, current_percent = int(percent), int(current_percent)
                print(f"Ticker: {ticker}, percent:{percent}")
                try:
                    figi, lot, price = get_figi(ticker)
                    print(f"price: {price}")
                except Exception as e:
                    print("get figi Error: ", e)
                if figi:
                    order_quantity = int((total_capital * float(percent) / 100))
                    print(f"total capital: {total_capital}")
                    print(f"Percentage of capital: {order_quantity}, type:{type(order_quantity)}")
                    number_of_lots = math.floor(order_quantity / price / lot)

                    print(f"lots: {number_of_lots}, order_quantity: {order_quantity}")
                    print(f"current positions: {current_positions}")
                    current_quantity = int((total_capital * float(current_percent) / 100))  # Считаем процент от доступного капитала (прошлый цикл)

                    if ticker in current_positions:
                        #если процент в прошлом цикле такой же как и сейчас, то скип
                        if current_percent == percent:
                            print(f"Повтор текущей позиции:{ticker} - {percent}")

                        elif current_percent > percent: #сравниваем, прошлый процент (предыдущий цикл) и процент, который мы приняли в аргументе словарем (если предыдущий процент больше текущего)

                            try:
                                with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
                                    if sandbox_mode:
                                        sb: SandboxService = client.sandbox
                                        r = sb.post_sandbox_order(
                                            figi=figi,
                                            quantity=math.floor(((current_quantity - order_quantity) / price) / lot), # current_quantity = 120000 - order_quantity = 100000 (20k)/price/lot = кол-во лотов для продажи, ибо они лишние
                                            # price=Quotation(units=1, nano=0),
                                            account_id=Tokens.account_sandbox_id,
                                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                                            order_type=OrderType.ORDER_TYPE_MARKET
                                        )
                                        print(f"Заявка на продажу {((current_quantity - order_quantity) / price)} акций {ticker} отправлена: {r}")
                                        
                                    else:
                                        r = client.orders.post_order(
                                            figi=figi,
                                            quantity=math.floor(((current_quantity - order_quantity) / price) / lot),
                                            account_id=Tokens.account_main_id,
                                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                                            order_type=OrderType.ORDER_TYPE_MARKET
                                        )
                                        print(f"Заявка на продажу {(current_quantity - order_quantity) / price} акций {ticker} отправлена: {r}")
                                    
                            except RequestError as e:
                                print(f"Ошибка при отправке заявки: {str(e)}")

                        # elif current_percent < percent (типо процент стал больше и нужно еще докупить) quantity=math.floor(((order_quantity - current_quantity) / price) / lot) //// order_quantity = 120000 - current_quantity = 100000 (на 20k еще докупит)
                        # предыдущий процент меньше текущего (докупаем)
                        elif current_percent < percent:
                            if not get_available_money() < order_quantity:
                                try:
                                    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
                                            if sandbox_mode:
                                                sb: SandboxService = client.sandbox
                                                r = sb.post_sandbox_order(
                                                    figi=figi,
                                                    quantity=math.floor(((order_quantity - current_quantity) / price) / lot), 
                                                    # price=Quotation(units=1, nano=0),
                                                    account_id=Tokens.account_sandbox_id,
                                                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                    order_type=OrderType.ORDER_TYPE_MARKET
                                                )
                                                print(f"Заявка на покупку {math.floor(((order_quantity - current_quantity) / price))} акций {ticker} отправлена: {r}")
                                            else:
                                                r = client.orders.post_order(
                                                    figi=figi,
                                                    quantity=math.floor(((order_quantity - current_quantity) / price) / lot),
                                                    account_id=Tokens.api_main_tinkoff,
                                                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                    order_type=OrderType.ORDER_TYPE_MARKET
                                                )
                                                print(f"Заявка на покупку {math.floor(((order_quantity - current_quantity) / price))} акций {ticker} отправлена: {r}")

                                except RequestError as e:
                                    print(f"Ошибка при отправке заявки: {str(e)}")
               
                    else:
                        try:
                            if not get_available_money() < order_quantity:
                                with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
                                        if sandbox_mode:
                                            sb: SandboxService = client.sandbox
                                            r = sb.post_sandbox_order(
                                                figi=figi,
                                                quantity=number_of_lots, 
                                                # price=Quotation(units=1, nano=0),
                                                account_id=Tokens.account_sandbox_id,
                                                direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                order_type=OrderType.ORDER_TYPE_MARKET
                                            )
                                            print(f"Заявка на покупку {number_of_lots*lot} акций {ticker} отправлена: {r}")
                                        else:
                                            r = client.orders.post_order(
                                                figi=figi,
                                                quantity=number_of_lots,
                                                account_id=Tokens.api_main_tinkoff,
                                                direction=OrderDirection.ORDER_DIRECTION_BUY,
                                                order_type=OrderType.ORDER_TYPE_MARKET
                                            )
                                            print(f"Заявка на покупку {number_of_lots*lot} акций {ticker} отправлена: {r}")
                        except RequestError as e:
                            print(f"Ошибка при отправке заявки: {str(e)}")
    
    def sell_all(sandbox_mode=True):
        with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:

                if sandbox_mode:
                    sb: SandboxService = client.sandbox
                    re = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)

                    for i in re.positions:
                        if i.instrument_type == 'share':

                            print(f"Share data:{i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)}")

                            r = sb.post_sandbox_order(
                                figi=i.figi,
                                quantity=i.quantity.units, 
                                # price=Quotation(units=1, nano=0),
                                account_id=Tokens.account_sandbox_id,
                                direction=OrderDirection.ORDER_DIRECTION_SELL,
                                order_type=OrderType.ORDER_TYPE_MARKET
                            )
                            print(f"Заявка на продажу {i.quantity.units} акций {i.figi} отправлена: {r}")
                            time.sleep(42)

                else:
                    r=client.operations.get_portfolio(account_id=Tokens.account_main_id)
                    for i in r.positions:
                        if i.instrument_type == 'share':
                            print(f"Share data:{i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)}")
                            r = client.orders.post_order(
                                figi=i.figi,
                                quantity=i.quantity.units,
                                account_id=Tokens.api_main_tinkoff,
                                direction=OrderDirection.ORDER_DIRECTION_SELL,
                                order_type=OrderType.ORDER_TYPE_MARKET
                            )
                            print(f"Заявка на продажу {i.quantity.units} акций {i.figi} отправлена: {r}")
                            time.sleep(20)

    def get_portfolio(sandbox_mode=True):
        with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
            if sandbox_mode:
                sb : SandboxService() = cl.sandbox
                account_id = Tokens.account_sandbox_id  # Замените на свой ID аккаунта песочницы
                r = sb.get_sandbox_portfolio(account_id=account_id)
            else:
                r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            return r