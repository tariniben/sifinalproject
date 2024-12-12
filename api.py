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

#Function to get news articles 

# World News API key
world_news_api_key = '1374cdc0145a436bae573e25d61ad392'

# List of company names for which we need news
company_names = ["Apple", "Google", "Amazon", "Microsoft"]

# Function to get the latest 25 news articles for a company using World News API
def get_latest_news(company_name):
    url = f"https://newsapi.org/v2/everything?q={company_name}&pageSize=25&apiKey={world_news_api_key}"
    
    # Make the API request
    response = requests.get(url)
    news_data = response.json()

    # Check if there is an error in the response
    if news_data.get('status') != 'ok':
        print(f"Error fetching news for {company_name}")
        return []

    # Collect and return the news articles data
    news_articles = []
    for article in news_data['articles']:
        news_articles.append({
            "company": company_name,
            "title": article['title'],
            "description": article['description'],
            "url": article['url'],
            "published_at": article['publishedAt']
        })
    
    return news_articles

# Function to process all companies and get their news articles
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Sentiment Analyzer Initialization
analyzer = SentimentIntensityAnalyzer()

# World News API key
world_news_api_key = '1374cdc0145a436bae573e25d61ad392'

# List of company names for which we need news
company_names = ["Apple", "Google", "Amazon", "Microsoft"]

# Function to get the latest 25 news articles for a company using World News API
def get_latest_news(company_name):
    url = f"https://newsapi.org/v2/everything?q={company_name}&pageSize=25&apiKey={world_news_api_key}"
    
    # Make the API request
    response = requests.get(url)
    news_data = response.json()

    # Check if there is an error in the response
    if news_data.get('status') != 'ok':
        print(f"Error fetching news for {company_name}")
        return []

    # Collect and return the news articles data
    news_articles = []
    for article in news_data['articles']:
        # Get polarity of the article's description/title (combined)
        text = article['title'] + " " + (article['description'] or "")
        sentiment = analyzer.polarity_scores(text)

        news_articles.append({
            "company": company_name,
            "title": article['title'],
            "description": article['description'],
            "url": article['url'],
            "published_at": article['publishedAt'],
            "polarity": sentiment['compound']  # Sentiment polarity score
        })
    
    return news_articles

# Function to process all companies and get their news articles
def process_companies_news(companies):
    all_news_articles = []

    for company_name in companies:
        print(f"Processing news for {company_name}...")
        
        # Get the latest 25 news articles for the company
        news_data = get_latest_news(company_name)
        all_news_articles.extend(news_data)

    # Print all results (or store in a database as needed)
    print("\nLatest News Articles with Polarity:")
    print(json.dumps(all_news_articles, indent=2))
    
    return all_news_articles

# Run the process for the company names
news_table = process_companies_news(company_names)


#functions for tables 


# Function to create and populate the database with the three tables
def create_tables():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('companies.db')
    cursor = conn.cursor()

    # Create the tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_table (
        company_id INTEGER PRIMARY KEY,
        symbol TEXT,
        name TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insider_table (
        company_id INTEGER,
        insider_senti TEXT,
        date TEXT,
        FOREIGN KEY(company_id) REFERENCES company_table(company_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS market_cap_table (
        company_id INTEGER,
        market_cap REAL,
        date TEXT,
        FOREIGN KEY(company_id) REFERENCES company_table(company_id)
    )
    ''')

    symbols = user_input()
    
    # Insert data into the company_table
    for idx, symbol in enumerate(symbols):
        name = get_name(symbol)
        cursor.execute('''
        INSERT INTO company_table (company_id, symbol, name) 
        VALUES (?, ?, ?)
        ''', (idx + 1, symbol, name))

    # Insert data into the insider_table
    for idx, symbol in enumerate(symbols):
        insider_senti = get_insider_senti(symbol)
        for item in insider_senti:
            cursor.execute('''
            INSERT INTO insider_table (company_id, insider_senti, date) 
            VALUES (?, ?, ?)
            ''', (idx + 1, item["insider_senti"], item["date"]))

    # Insert data into the market_cap_table
    for idx, symbol in enumerate(symbols):
        market_cap_data = get_market_cap(symbol)
        for item in market_cap_data:
            cursor.execute('''
            INSERT INTO market_cap_table (company_id, market_cap, date) 
            VALUES (?, ?, ?)
            ''', (idx + 1, item["market_cap"], item["date"]))

    # Commit the changes and close the connection
    conn.commit()

    # Query the tables to confirm the data insertion
    cursor.execute('SELECT * FROM company_table')
    company_table = cursor.fetchall()

    cursor.execute('SELECT * FROM insider_table')
    insider_table = cursor.fetchall()

    cursor.execute('SELECT * FROM market_cap_table')
    market_cap_table = cursor.fetchall()

    # Close the connection
    conn.close()

    return company_table, insider_table, market_cap_table


# Example of usage
company_table, insider_table, market_cap_table = create_tables()

# Print the tables
print("Table 1: Company Table")
print(json.dumps(company_table, indent=2))
print("\nTable 2: Insider Sentiment Table")
print(json.dumps(insider_table, indent=2))
print("\nTable 3: Market Cap Table")
print(json.dumps(market_cap_table, indent=2))

