from datetime import datetime
from api_keys import Tokens
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, Quotation, InstrumentIdType
from tinkoff.invest.services import InstrumentsService, MarketDataService
from pandas import DataFrame
import math
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
            print(r.total_amount_currencies.units)


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
        # df.to_json()
        # print(df.tail(1))
    
        df = df[df['ticker'] == Ticker]
        if df.empty:
            print(f"Нет тикера {Ticker}")
            return

        result_lot = df['lot'].iloc[0]
        print(f"lots {result_lot}")
        # print(df.iloc[0])
        result_figi = df['figi'].iloc[0]
        print(result_figi, type(result_figi))
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
            print("Get available_money...")
            available_money = get_available_money(sandbox_mode)
            print("successfully")
        except Exception as ex:
            print(f"Error get_available_money: {ex}")
        for current_ticker, current_percent in real_positions.items(): # НЕ РАБОТАЕТ ИЗ ЗА ТОГО ЧТО ЦИКЛ ИДЕТ ПО ПУСТОМУ СЛОВАРЮ
            for ticker, percent in order_dict.items():
                print(f"Ticker: {ticker}, percent:{percent}")
                try:
                    figi, lot, price = get_figi(ticker)
                    print(f"price: {price}")
                except Exception as e:
                    print("get figi Error: ", e)
                if figi:
                    order_quantity = int((available_money * float(percent) / 100))
                    print(f"available money: {available_money}")
                    print(f"Percentage of capital: {order_quantity}, type:{type(order_quantity)}")
                    number_of_lots = math.floor(order_quantity / price / lot)

                    print(f"lots: {number_of_lots}, order_quantity: {order_quantity}")
                    print(f"current positions: {current_positions}")
                    current_quantity = int((available_money * float(current_percent) / 100))  # Считаем процент от доступного капитала (прошлый цикл)

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
                    r = sb.post_sandbox_order(
                        figi="figi",
                        quantity=0, 
                        # price=Quotation(units=1, nano=0),
                        account_id=Tokens.account_sandbox_id,
                        direction=OrderDirection.ORDER_DIRECTION_BUY,
                        order_type=OrderType.ORDER_TYPE_MARKET
                    )
                    print(f"Заявка на продажу {0} акций {0} отправлена: {r}")
                else:
                    r = client.orders.post_order(
                        figi="figi",
                        quantity=0,
                        account_id=Tokens.api_main_tinkoff,
                        direction=OrderDirection.ORDER_DIRECTION_BUY,
                        order_type=OrderType.ORDER_TYPE_MARKET
                    )
                    print(f"Заявка на продажу {0} акций {0} отправлена: {r}")

