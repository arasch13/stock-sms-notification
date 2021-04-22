import requests
from twilio.rest import Client
import os


STOCK = "QS"
COMPANY_NAME = "QuantumScape Corporation"

MY_NUMBER = os.environ["MY_MOBILE_NUMBER"]

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ["MY_STOCK_API_KEY"]

NEWS_ENDPOINT = "http://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ["MY_NEWS_API_KEY"]

SMS_SID = os.environ["TWILIO_SID"]
SMS_AUTH_TOKEN = os.environ["TWILIO_TOKEN"]
SMS_NUMBER = os.environ["TWILIO_NUMBER"]

# -------------------------------------------- STOCK PRIZE ----------------------------------------------------------

# make API call
parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}
response = requests.get(url=STOCK_ENDPOINT, params=parameters)
response.raise_for_status()

# get stock prize of last two days and calculate absolute change
data = response.json()
daily_data = data['Time Series (Daily)']
days = list(daily_data.keys())
value_today = float(daily_data[days[0]]['4. close'])
value_before = float(daily_data[days[1]]['4. close'])
stock_change = (abs(value_today - value_before) / value_before) * 100.0
absolute_stock_change = abs(stock_change)
if absolute_stock_change >= 5:
    significant_change = True
else:
    significant_change = False

# -------------------------------------------- STOCK NEWS -----------------------------------------------------------

if significant_change:
    parameters = {
        "sortBy": "popularity",
        "q": COMPANY_NAME,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url=NEWS_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()
    top_articles = {}
    for index in range(3):
        top_articles[index] = {"title": data['articles'][index]['title'],
                               "description": data['articles'][index]['description']}

# --------------------------------------------- SEND SMS ------------------------------------------------------------

if significant_change:
    rounded_absolute_stock_change = round(absolute_stock_change, 1)
    if stock_change > 0:
        sign = "🔺"
    elif stock_change < 0:
        sign = "🔻"
    else:
        sign = ""
    for article_nr in top_articles:
        message = f"{STOCK}: {sign}{rounded_absolute_stock_change}%\n" \
                  f"Headline: {top_articles[article_nr]['title']}\n" \
                  f"Brief: {top_articles[article_nr]['description']}"
        account_sid = SMS_SID
        auth_token = SMS_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=SMS_NUMBER,
            to=MY_NUMBER
        )
