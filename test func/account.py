from datetime import timedelta
from tinkoff.invest import Client, CandleInterval
from api_keys import Tokens
from tinkoff.invest.utils import now

TOKEN = Tokens.api_sandbox_tinkoff

days_back = 60

with Client(TOKEN) as client:
    # print(client.users.get_info())
    print(client.users.get_accounts())
    # print(client.operations.get_positions(account_id='2036486835'))
    # получаем бары по акцее 
    # print(client.market_data.get_candles(figi="BBG004730RP0", from_=now() - timedelta(days=days_back), to=now(), interval=CandleInterval.CANDLE_INTERVAL_DAY))
