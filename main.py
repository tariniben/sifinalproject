import requests
import json
import finnhub
finnhub_client = finnhub.Client(api_key="ct4kj9hr01qo7vqao18gct4kj9hr01qo7vqao190")

#print(finnhub_client.symbol_lookup('AAPL'))
#print(finnhub_client.stock_insider_sentiment('AAPL', '2021-01-01', '2022-03-01'))

def user_input():
    symbol_list = []
    for i in range(2):
        symbol = input("Enter a company's stock symbol: ")
        symbol_list.append(symbol.upper())

    return symbol_list

def get_name(lst):
    name_list = []
    for symbol in lst:
        company_name = finnhub_client.symbol_lookup(symbol)["result"][0]["description"]
        name_list.append(company_name)
    
    return name_list

symbol_list = user_input()
print(get_name(symbol_list))