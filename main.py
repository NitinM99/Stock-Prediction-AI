import yfinance as yf
import pandas as pd
import datetime as dt
import streamlit as st

def get_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1d')['Close']
    if not data.empty:
        return data.iloc[-1]
   

def get_5yr_ago(ticker):
    today = dt.date.today()
    five_years_ago = today.replace(year=today.year - 5)
    data = yf.Ticker(ticker).history(start=five_years_ago, end=today)['Close']
    if not data.empty:
        return data.mean()
   

def get_5yrEPS_percent(ticker):
    current = get_stock_price(ticker)
    ago = get_5yr_ago(ticker)
    return ((current - ago) / ago) * 100
    

def get_1yr_ago(ticker):
    today = dt.date.today()
    one_year_ago = today.replace(year=today.year - 1)
    data = yf.Ticker(ticker).history(start=one_year_ago, end=today)
    return data['Close'].mean()

def get_1yr_EPS(ticker):
    Current = get_stock_price(ticker)
    Ago = get_1yr_ago(ticker)
    return ((Current - Ago) / Ago) * 100

def calculate_rsi(ticker, window=14):
    data = yf.Ticker(ticker).history(period=f'{window}d')['Close']
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window - 1, adjust=False).mean()
    ema_down = down.ewm(com=window - 1, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_ninety_SMA(ticker):
    data = yf.Ticker(ticker).history(period='3mo')['Close'].mean()
    return data

def get_ninety_low(ticker):
    data = yf.Ticker(ticker).history(period='3mo')['Low'].min()
    return data

def compare_ninetys(ticker):
    Low = get_ninety_low(ticker)
    Avg = get_ninety_SMA(ticker)
    return ((Avg - Low) / Low) * 100

def calculate_SMA(ticker, window=26):
    data = yf.Ticker(ticker).history(period=f'{window}d')['Close'].mean()
    return data

def calculate_EMA(ticker, window=12):
    data = yf.Ticker(ticker).history(period=f'{window}d')['Close'].ewm(span=window, adjust=False).mean()
    return data.iloc[-1]

def MACD(ticker):
    SMA = calculate_SMA(ticker)
    EMA = calculate_EMA(ticker)
    return EMA - SMA

def get_TwoHundred_ago(ticker):
    today = dt.date.today()
    two_hundred_days_ago = today - dt.timedelta(days=200)
    data = yf.Ticker(ticker).history(start=two_hundred_days_ago, end=today)
    return data['Close'].mean()

def get_TwoHundredEPSPer(ticker):
    Old = get_TwoHundred_ago(ticker)
    Now = get_stock_price(ticker)
    return ((Now - Old) / Old) * 100

def get_Twelve_day_ago_EPS(ticker):
    today = dt.date.today()
    twelve_days_ago = today - dt.timedelta(days=12)
    data = yf.Ticker(ticker).history(start=twelve_days_ago, end=today)['Close']
    Current = get_stock_price(ticker)
    TwelveAgo = data.mean()
    return ((Current - TwelveAgo) / TwelveAgo) * 100

def Compare_EPS(ticker):
    Twelve = get_Twelve_day_ago_EPS(ticker)
    Twoh = get_TwoHundredEPSPer(ticker)
    return Twelve - Twoh

def get_Twohundredday_SMA(ticker):
    return calculate_SMA(ticker, 200)

def CompMVG(ticker):
    Twoh = get_Twohundredday_SMA(ticker)
    EMA = calculate_EMA(ticker)
    SMA = calculate_SMA(ticker)
    return EMA > SMA > Twoh

def volatility(ticker):
    SMA = calculate_SMA(ticker)
    data = yf.Ticker(ticker).history(period='26d')
    SMALow = data['Close'].min()
    return ((SMA - SMALow) / SMALow) * 100

def Seven_Day_growth(ticker):
    today = dt.date.today()
    seven_days_ago = today - dt.timedelta(days=7)
    data = yf.Ticker(ticker).history(start=seven_days_ago, end=today)['Close']
    return ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100

def DayTwoMinus_DayOneMinus(ticker):
    today = dt.date.today()
    data = yf.Ticker(ticker).history(start=today - dt.timedelta(days=3), end=today)['Close']
    return data.iloc[-1] - data.iloc[-2]

def Now_DayOneMinus(ticker):
    today = dt.date.today()
    data = yf.Ticker(ticker).history(start=today - dt.timedelta(days=2), end=today)['Close']
    return get_stock_price(ticker) - data.iloc[-1]

# Calculation functions for short term and long term scores are omitted for brevity


def calculate_short_term_score(ticker):
    score = 0

    # RSI
    rsi = calculate_rsi(ticker)
    score += 1 if 30 <= rsi <= 50 else 0
        


    # MACD Positive
    macd = MACD(ticker)
    score += 1 if macd > 0 else 0
        

    Twelve= get_Twelve_day_ago_EPS(ticker)
    Twoh= get_Twelve_day_ago_EPS(ticker)
    score += 1 if Twelve>Twoh else 0

    # EMA vs SMA vs 200-Day SMA Comparison
    # Assuming function for this comparison is defined
    EMA=calculate_EMA(ticker)
    SMA=calculate_SMA(ticker)
    Twoh=get_Twohundredday_SMA(ticker)
    score += 1 if EMA>SMA>Twoh else 0

    # Volatility
    # Assuming function for volatility is defined
    stock_volatility = volatility(ticker)
    score += 1 if stock_volatility < 20 else 0

    # 7-Day Growth
    # Assuming function for 7-day growth is defined
    seven_day_growth = Seven_Day_growth(ticker)
    score += 1 if seven_day_growth < 20 else 0
    score += 0.5 if seven_day_growth > 20 else 0
            
    data= score/6
    return data
    
def calculate_long_term_score(ticker):
    score = 0
    ninety_day_comparison = compare_ninetys(ticker)
    if ninety_day_comparison < 20:
        score += 1

    eps_growth_5yr = get_5yrEPS_percent(ticker)
    if eps_growth_5yr > 50:
        score += 1

    eps_growth_1yr = get_1yr_EPS(ticker)
    if eps_growth_1yr > 7.5:
        score += 1

    rsi = calculate_rsi(ticker)
    if 40 <= rsi <= 60:
        score += 1

    return score / 4


# Example Usage
ticker = 'AAPL'  # Replace with your desired ticker
long_term_score = calculate_long_term_score(ticker)
print(f"Normalized Long-Term Score for {ticker}: {long_term_score}")

def app():
    st.title('Stock Analysis Tool')
    ticker = st.text_input('Enter a stock ticker (e.g., AAPL):').upper()

def app():
    st.title('Stock Analysis Tool')
    ticker = st.text_input('Enter a stock ticker (e.g., AAPL):').upper()

def app():
    st.title('Stock Analysis Tool')
    ticker = st.text_input('Enter a stock ticker (e.g., AAPL):').upper()

    if st.button('Analyze'):
        if ticker:
            try:
                long_score = calculate_long_term_score(ticker)
                short_score = calculate_short_term_score(ticker)
                trailing_EPS = get_1yr_EPS(ticker)
                volatility_value = volatility(ticker)
                sma_value = calculate_SMA(ticker)
                macd_value = MACD(ticker)
                rsi_value = calculate_rsi(ticker)

                st.success(f"Results for {ticker}:")
                st.write(f"SMA: {sma_value}")
                st.write(f"Volatility Percent: {volatility_value}")
                st.write(f"MACD: {macd_value}")
                st.write(f"RSI: {rsi_value}")
                st.write(f"1 Year EPS: '{trailing_EPS}'")
                st.write(f"Long Term Score: {long_score}")
                st.write(f"Short Term Score: {short_score}")

                
                long_investment_decision = "Good investment long term" if long_score > 0.65 else "Don't invest long term"
                st.write(long_investment_decision)
               
                short_investment_decision = "Good investment short term" if short_score > 0.65 else "Don't invest short term"
                st.write(short_investment_decision)

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a valid stock ticker.")

if __name__ == '__main__':
    app()
