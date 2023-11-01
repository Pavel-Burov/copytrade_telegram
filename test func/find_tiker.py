import requests

def find_ticker_by_company_name(api_key, company_name):
    base_url = "https://www.alphavantage.co/query"
    function = "SYMBOL_SEARCH"
    
    params = {
        "function": function,
        "keywords": company_name,
        "apikey": api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if "bestMatches" in data:
        best_match = data["bestMatches"][0]
        ticker = best_match["1. symbol"]
        return ticker
    else:
        return None

# Замените 'YOUR_API_KEY' на свой API ключ Alpha Vantage
api_key = "3GF0M41U6WOFBGCC"
company_name = "Apple"  # Замените на название компании, которую вы ищете
ticker = find_ticker_by_company_name(api_key, company_name)

if ticker:
    print(f"Тикер акций для {company_name}: {ticker}")
else:
    print(f"Не удалось найти тикер для {company_name}")
