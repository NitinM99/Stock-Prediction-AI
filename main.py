import yahoofinance as yf
import pandas as pd
import streamlit as st

def calculate_SMA(ticker, period='26d'):
    return yf.Ticker(ticker).history(period=period)['Close'].mean()

def calculate_EMA(ticker, span=12):
    data = yf.Ticker(ticker).history(period=f'{span}d')['Close']
    return data.ewm(span=span, adjust=False).mean().iloc[-1]

def calculate_MACD(ticker):
    sma = calculate_SMA(ticker)
    ema = calculate_EMA(ticker)
    return ema - sma

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

def get_stock_price(ticker):
    return yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]

def get_200d_price(ticker):
    data = yf.Ticker(ticker).history(period='200d')['Close']
    return data.iloc[-1]

def mean_200d(ticker):
    return yf.Ticker(ticker).history(period='200d')['Close'].mean()

def volatility_score(ticker):
    data = yf.Ticker(ticker).history(period='200d')
    low = data['Low'].min()
    avg = data['Close'].mean()
    score = avg / low  # A higher score indicates more variability
    return score

def PE(ticker):
    price = get_stock_price(ticker)
    twoh_price = get_200d_price(ticker)
    eps = (price - twoh_price) / twoh_price
    return eps

def short_stock_Score(ticker, rsi_window=14):
    RSI = calculate_rsi(ticker, rsi_window)
    macd = calculate_MACD(ticker)
    variance = volatility_score(ticker)
    score = 0

    score += 1 if RSI < 50 else 0
    score += 1 if macd > 1 else 0
    score += 1 if variance < 1.2 else 0

    final_score = score / 3
    return str(final_score), "Not worth it" if final_score < 0.6 else "Worth it"

def get_4yr_ago(ticker):
    data = yf.Ticker(ticker).history(period='4y')['Close']
    return data.iloc[-1]

def long_stock_score(ticker):
    current_price = get_stock_price(ticker)
    price_200d_ago = get_200d_price(ticker)
    eps = PE(ticker)
    variance = volatility_score(ticker)
    price_4yr_ago = get_4yr_ago(ticker)

    score = 0

    if current_price > price_200d_ago * 1.05:
        score += 1

    if ((current_price - price_4yr_ago) / price_4yr_ago) > 0.20:
        score += 1

    score += 1 if variance < 1.2 else 0
    score += 1 if eps < 15 else 0

    final_score = score / 4
    return str(final_score), "Good for long-term investment" if final_score > 0.6 else "Risky for long-term investment"

def main():
    st.title("Stock Analysis App")

    ticker = st.text_input("Enter the ticker symbol:", "AAPL")

    if st.button("Analyze"):
        try:
            price = get_stock_price(ticker)
            st.write(f"Current Price of {ticker}: ${price}")

            mean_price_200d = mean_200d(ticker)
            st.write(f"200-day Mean Price of {ticker}: ${mean_price_200d}")

            macd = calculate_MACD(ticker)
            st.write(f"MACD of {ticker}: {macd}")

            short_score, short_recommendation = short_stock_Score(ticker)
            st.write(f"Short Stock Score of {ticker}: {short_score} ({short_recommendation})")

            variance = volatility_score(ticker)
            st.write(f"Volatility of {ticker}: {variance}")

            long_score, long_recommendation = long_stock_score(ticker)
            st.write(f"Long Stock Score of {ticker}: {long_score} ({long_recommendation})")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
