from datetime import datetime
from api_keys import Tokens
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, Quotation
from tinkoff.invest.services import InstrumentsService, MarketDataService
from pandas import DataFrame

from tinkoff.invest.services import SandboxService

def cast_money(v):
    return v.units + v.nano / 1e9

def get_available_money():
    with Client(Tokens.api_sandbox_tinkoff) as cl:
        sb : SandboxService = cl.sandbox
        account_id = '6454aceb-d162-4a5c-9836-24e734ee8630'

        r = sb.get_sandbox_portfolio(account_id=account_id)

        return r.total_amount_currencies.nano


def get_figi(ticker):
    with Client(Tokens.api_main_tinkoff) as cl:
        instruments = cl.instruments
        for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
            for item in getattr(instruments, method)().instruments:
                if item.ticker == ticker:
                    return item.figi
        print(f"Нет тикера {ticker}")
        return None

def get_current_positions():
    with Client(Tokens.api_main_tinkoff) as client:
        portfolio = client.portfolio.portfolio(Tokens.api_main_tinkoff)
        positions = {}
        for position in portfolio.positions:
            positions[position.ticker] = position
        # return positions
        # return real_positions
"""
def process_orders(order_dict, available_money):
    for ticker, percent in order_dict.items():
        figi = get_figi(ticker)
        if figi:
            order_quantity = int(available_money * float(percent) / 100)
            try:
                with Client(Tokens.api_main_tinkoff) as client:
                    r = client.orders.post_order(
                        order_id=str(datetime.utcnow().timestamp()),
                        figi=figi,
                        quantity=order_quantity,
                        account_id=Tokens.api_main_tinkoff,
                        direction=OrderDirection.ORDER_DIRECTION_BUY,  # ORDER_DIRECTION_BUY or ORDER_DIRECTION_SELL
                        order_type=OrderType.ORDER_TYPE_MARKET
                    )
                    print(f"Заявка на покупку {order_quantity} акций {ticker} отправлена: {r}")
            except RequestError as e:
                print(f"Ошибка при отправке заявки: {str(e)}")
"""

def process_orders(order_dict,  real_positions):
    # current_positions = get_current_positions()
    current_positions = real_positions
    available_money = get_available_money()
    
    for ticker, percent in order_dict.items():
        figi = get_figi(ticker)
        if figi:
            order_quantity = int(available_money * float(percent) / 100)
            if ticker in current_positions:
                current_quantity = current_positions[ticker].balance
                if current_quantity > order_quantity:
                    try:
                        with Client(Tokens.api_main_tinkoff) as client:
                            r = client.orders.post_order(
                                order_id=str(datetime.utcnow().timestamp()),
                                figi=figi,
                                quantity=current_quantity - order_quantity,
                                account_id=Tokens.api_main_tinkoff,
                                direction=OrderDirection.ORDER_DIRECTION_SELL,
                                order_type=OrderType.ORDER_TYPE_MARKET
                            )
                            print(f"Заявка на продажу {current_quantity - order_quantity} акций {ticker} отправлена: {r}")
                    except RequestError as e:
                        print(f"Ошибка при отправке заявки: {str(e)}")
            else:
                try:
                    with Client(Tokens.api_main_tinkoff) as client:
                        r = client.orders.post_order(
                            order_id=str(datetime.utcnow().timestamp()),
                            figi=figi,
                            quantity=order_quantity,
                            account_id=Tokens.api_main_tinkoff,
                            direction=OrderDirection.ORDER_DIRECTION_BUY,
                            order_type=OrderType.ORDER_TYPE_MARKET
                        )
                        print(f"Заявка на покупку {order_quantity} акций {ticker} отправлена: {r}")
                except RequestError as e:
                    print(f"Ошибка при отправке заявки: {str(e)}")



# Пример использования:
order_dict = {'SBER': '18', 'PAL': '16'}
available_money = 10000  # Замените на доступное у вас количество денег
process_orders(order_dict, available_money)
