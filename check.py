from api_keys import Tokens
from tinkoff.invest import Client, InstrumentStatus, CandleInterval


with Client(Tokens.api_main_tinkoff) as client:
    # r = client.users.get_accounts()
    # print(r)
    #id='2036486835'
    r = client.operations.get_portfolio(account_id='2036486835')
    print(r.total_amount_currencies.units)