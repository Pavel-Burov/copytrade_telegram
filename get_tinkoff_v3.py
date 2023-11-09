from datetime import datetime
from api_keys import Tokens
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, Quotation, InstrumentIdType
from tinkoff.invest.services import InstrumentsService, MarketDataService
from pandas import DataFrame
import math, time
import pandas as pd
from tinkoff.invest.services import SandboxService



def cast_money(v):
    return v.units + v.nano / 1e9

def get_total_capital(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            return cast_money(r.total_amount_portfolio)
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            return cast_money(r.total_amount_portfolio)

def get_available_money(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            return r.total_amount_currencies.units
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            return r.total_amount_currencies.units

def get_positions(sandbox_mode=True):
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as cl:
        if sandbox_mode:
            sb : SandboxService = cl.sandbox
            r = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
            for i in r.positions:
                # if i.instrument_type == 'share':
                print(f"figi: {i.figi}, quantity: {i.quantity.units}, average_postions_price: {cast_money(i.average_position_price)}, current price: {cast_money(i.current_price)}\n")
        else:
            r = cl.operations.get_portfolio(account_id=Tokens.account_main_id)
            for i in r.positions:
                # if i.instrument_type == 'share':
                print(f"figi: {i.figi}, quantity: {i.quantity.units}, average_postions_price: {cast_money(i.average_position_price)}, current price: {cast_money(i.current_price)}\n")


def get_shares_data(ticker):
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

        df = df[df['ticker'] == ticker.upper()]
        if df.empty:
            print(f"Нет тикера {ticker}")
            return None

        result_lot = df['lot'].iloc[0]
        result_figi = df['figi'].iloc[0]
        price = market_data.get_last_prices(figi=[result_figi])
        last_price = cast_money(price.last_prices[0].price)

        return result_figi, result_lot, last_price


def buy(ticker, sandbox_mode=True):
    figi, lot, price = get_shares_data(ticker)

    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
        if sandbox_mode:
            sb: SandboxService = client.sandbox
            account_id = Tokens.account_sandbox_id
        else:
            account_id = Tokens.api_main_tinkoff

        quantity = int(math.floor(get_available_money(sandbox_mode=sandbox_mode) * 20 / 100 / price / lot)) # покупаем на 20% от доступных денег
        
        # Отправляем рыночный ордер на покупку
        if sandbox_mode:
            r = sb.post_sandbox_order(
                figi=figi,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
        else:
            r = client.orders(
                figi=figi,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
        
        print(f"Заявка на покупку {quantity * lot} акций {ticker} отправлена: {r}")

        # Предполагаем, что мы получаем цену исполнения из ответа r
        execution_price = cast_money(r.total_order_amount)  # цена из запроса
        print(f'Завершена покупка акций на сумму: {execution_price}')

        # Рассчитываем стоп-лосс цену
        stop_loss_percentage = 0.5309033281 / 100
        stop_loss_price = execution_price * (1 - stop_loss_percentage)

        # Конвертируем стоп-лосс цену в нужный формат
        stop_loss_price_units = int(stop_loss_price)  # Целая часть цены
        stop_loss_price_nano = int((stop_loss_price - stop_loss_price_units) * 1e9)  # Дробная часть цены, переведенная в нано

        stop_loss_price_quotation = Quotation(units=stop_loss_price_units, nano=stop_loss_price_nano)

        # print(f"Stop Loss Price Quotation: {stop_loss_price_quotation.units} units, {stop_loss_price_quotation.nano} nano")

        # Отправляем стоп-лосс ордер
        try:
            if sandbox_mode:
                stop_order_response = sb.post_sandbox_order(
                    figi=figi,
                    quantity=quantity,
                    price=stop_loss_price_quotation,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                stop_order_response = client.stop_orders.post_stop_order(
                    figi=figi,
                    quantity=quantity,
                    price=stop_loss_price_quotation,
                    stop_price=stop_loss_price_quotation,
                    account_id=account_id,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            print(f"Стоп-лосс ордер установлен на цену {cast_money(stop_loss_price)}: {stop_order_response}")
        except Exception as e:
            print(f"Ошибка при установке стоп-лосс ордера: {e}")


def sell(ticker, sandbox_mode=True):
    figi, lot, price = get_shares_data(ticker)
    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
            if sandbox_mode:
                sb: SandboxService = client.sandbox
                re = sb.get_sandbox_portfolio(account_id=Tokens.account_sandbox_id)
                for i in re.positions:
                    if i.figi == figi:
                        print(f"Share data:{i.quantity_lots.units, i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)}")

                        r = sb.post_sandbox_order(
                            figi=i.figi,
                            quantity=i.quantity_lots.units, 
                            # price=Quotation(units=1, nano=0),
                            account_id=Tokens.account_sandbox_id,
                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                            order_type=OrderType.ORDER_TYPE_MARKET
                        )
                        print(f"Заявка на продажу {i.quantity.units} акций {i.figi} отправлена: {r}")

            else:
                r=client.operations.get_portfolio(account_id=Tokens.account_main_id)
                for i in r.positions:
                    if i.figi == figi:
                        print(f"Share data:{i.figi, i.quantity.units, cast_money(i.average_position_price), cast_money(i.current_price)}")
                        r = client.orders.post_order(
                            figi=i.figi,
                            quantity=i.quantity_lots.units,
                            account_id=Tokens.api_main_tinkoff,
                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                            order_type=OrderType.ORDER_TYPE_MARKET
                        )
                        print(f"Заявка на продажу {i.quantity.units} акций {i.figi} отправлена: {r}")


def short(ticker, sandbox_mode=True):
    figi, lot, price = get_shares_data(ticker)
    quantity = math.floor(get_available_money(sandbox_mode=sandbox_mode) * 20 / 100 / price / lot) # на 20% от доступных денег

    with Client(Tokens.api_sandbox_tinkoff if sandbox_mode else Tokens.api_main_tinkoff) as client:
            if sandbox_mode:
                sb: SandboxService = client.sandbox
                r = sb.post_sandbox_order(
                    figi=figi,
                    quantity=quantity, 
                    account_id=Tokens.account_sandbox_id,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
                print(f"Заявка на шорт {quantity*lot} акций {figi} отправлена: {r}")

            else:
                r = client.orders.post_order(
                    figi=figi,
                    quantity=quantity,
                    account_id=Tokens.api_main_tinkoff,
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
                print(f"Заявка на шорт {quantity*lot} акций {figi} отправлена: {r}")


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
                            quantity=i.quantity_lots.units, 
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
                            quantity=i.quantity_lots.units,
                            account_id=Tokens.api_main_tinkoff,
                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                            order_type=OrderType.ORDER_TYPE_MARKET
                        )
                        print(f"Заявка на продажу {i.quantity.units} акций {i.figi} отправлена: {r}")
                        time.sleep(20)


class Trade:
    def process_orders(result, sandbox_mode=True):
        # sell_all()
        for positions in result.items():
            ticker, process = positions
            if process.lower() == "buy":
                buy(ticker=ticker, sandbox_mode=sandbox_mode)
                get_positions()
            elif process.lower() == "sell":
                sell(ticker=ticker, sandbox_mode=sandbox_mode)
                get_positions()
            elif process.lower() == "short":
                short(ticker=ticker, sandbox_mode=sandbox_mode)
                get_positions()
            else:
                print("Не понял че покупать")