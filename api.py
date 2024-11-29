import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import finnhub
finnhub_client = finnhub.Client(api_key="ct4kj9hr01qo7vqao18gct4kj9hr01qo7vqao190")

#gets 4 company symbols from user
#input = nothing, output = list of company symbols
def user_input():
    symbol_list = []
    for i in range(4):
        symbol = input("Enter a company's stock symbol: ")
        symbol_list.append(symbol.upper())

    return symbol_list

#gets company name using company symbol
#input = symbol, output = company name
def get_name(symbol):
    company_name = finnhub_client.symbol_lookup(symbol)["result"][0]["description"]
    return company_name

#gets last 25 insider sentiment values for a company using company symbol
#input = symbol, output = list of dictionaries with insider sentiment & date
def get_insider_senti(symbol):
    all_insider_senti = finnhub_client.stock_insider_sentiment(symbol, '2000-01-01', datetime.now().strftime('%Y-%m-%d'))["data"]
    insider_senti = []
    if len(all_insider_senti) > 24:
        all_insider_senti = all_insider_senti[-25:]
    for item in all_insider_senti:
        senti = item['change']
        date_ = f"{item['year']}-{item['month']:02}"
        insider_senti.append(
            {
                'insider_senti': senti,
                'date': date_
            }
        )
    return insider_senti

# print(get_insider_senti("AAPL"))

#gets market cap for company across last 25 months using company symbol
#input = symbol, output = list of dictionaries with market cap & date
def get_market_cap(symbol):
    current_date = datetime.now()
    start_date = current_date - relativedelta(months=25)

    profit_data = requests.get(f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?from={datetime.strftime(start_date,"%Y-%m")}-01&to={datetime.strftime(current_date,"%Y-%m-%d")}&apikey=qhxCjz53DrEuhv4IeCuvYl9eg1Y13QJ3").json()[::-1]

    pointer = 0
    final_data = []
    for i in range(25):
        year_month_to_check = datetime.strftime(start_date + relativedelta(months=i), "%Y-%m")
        have_match = False
        while not have_match:
            if profit_data[pointer]["date"].startswith(year_month_to_check):
                final_data.append({
                    "date":year_month_to_check,
                    "market_cap":profit_data[pointer]["marketCap"]
                })
                break
            pointer += 1
    
    return final_data

#print(get_market_cap("AAPL"))
