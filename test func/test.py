from tinkoff.invest import Client
from tinkoff.invest.services import SandboxService, PortfolioRequest
from api_keys import Tokens

TOKEN = Tokens.api_sandbox_tinkoff # Replace with your Tinkoff API token
sandbox_account_id = Tokens.account_sandbox_id




def get_sandbox_total_portfolio_value(token):
    # Initialize the client with your token
    with Client(token) as client:
        # Initialize the sandbox service
        sandbox_service = SandboxService(client)

        # Retrieve the sandbox portfolio for the specified account ID
        portfolio_request = PortfolioRequest(account_id=sandbox_account_id)
        portfolio = sandbox_service.GetSandboxPortfolio(portfolio_request)
        
        # Calculate the total value of all shares in the portfolio
        total_value = sum(position.balance * position.average_position_price.units
                          for position in portfolio.positions if position.instrument_type == 'Share')
        
        # Retrieve the amount of available cash
        # Assuming the first money_amount is the available cash
        available_cash = portfolio.total_money_amount.units

        # Calculate the total capital in the portfolio
        total_capital = total_value + available_cash

        return total_capital

# Example usage:
# Get total portfolio value for the sandbox account
print(f"Total capital in the sandbox account: {get_sandbox_total_portfolio_value(TOKEN)}")