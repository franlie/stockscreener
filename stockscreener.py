# Import libraries
from numpy import nan as npNaN
import pandas as pd
import pandas_ta as ta
import datetime as dt
import streamlit as st
from pandas_datareader import data as pdr
import yfinance as yf
import plotly.graph_objects as go

@st.cache_data(ttl=7200)
def get_data(ticker):
    yf.pdr_override()

    start = dt.datetime(2021, 8, 1)
    end = dt.datetime.now()

    data = yf.download(ticker, start=start, end=end)
    return data

st.title("EMA Crossover Screener for Stocks")

st.sidebar.title("Screener Settings")
long_ma = st.sidebar.slider(
    'Select EMA for long period', 5, 200, step=5, value=20)

short_ma = st.sidebar.slider(
    'Select EMA for short period', 5, 200, step=5, value=10)

direction = st.sidebar.radio(
    'Select direction of crossing',  ('bullish', 'bearish'))
if direction == 'bullish':
    st.sidebar.write('<span style="color:yellow;"> -> </span><span style="color:red;">EMA ' + str(short_ma) + '</span> crossing <span style="color:green;">EMA ' + str(long_ma) + ' </span>upwards', unsafe_allow_html=True)
else:
    st.sidebar.write('<span style="color:yellow;"> -> </span><span style="color:red;">EMA ' + str(short_ma) + '</span> crossing <span style="color:green;">EMA ' + str(long_ma) + ' </span>downwards', unsafe_allow_html=True)

universe = st.sidebar.radio(
    'Select Stock Universe',  ('S&P 500', 'NASDAQ100', 'DAX'))


if st.sidebar.button("Scan"):

    if short_ma >= long_ma:
        st.write('<span style="color:red; font-style:bold;">Error: Short period EMA must be smaller than long period EMA</span>', unsafe_allow_html=True)
        st.write(short_ma)
        st.write(long_ma)
    else:   
        st.write("Scanning for EMA " + str(short_ma) + "/ EMA " + str(long_ma) + " " + direction +  " Crossovers in the " + universe +  " on last Trading Day")
    
        if universe == 'S&P 500':
            stocks = 'sp500'
        elif universe == "NASDAQ100":
            stocks = 'nasdaq100'
        else:
            stocks = 'dax'
        
        # Reading tickers from csv
        stocks = pd.read_csv(f"./tickers/{stocks}.csv")
        tickers = stocks["Symbol"].unique().tolist()

        # Progress Bar settings
        progress_text = "Scanning stocks..."
        my_bar = st.progress(0, text=progress_text)

        progress_counter = 0
        increment = 1/len(tickers)

        # Initializing counter for results
        counter = 0
        # Loop through each ticker and get the data
        for ticker in tickers:
            # Get the adjusted close price data
            try:
                data = get_data(ticker)
                progress_counter += increment
                my_bar.progress(progress_counter)
            except:
                pass

            # Calculate the 10-day and 20-day moving averages
            data["MA_short"] = data["Adj Close"].ewm(span=short_ma).mean()
            data["MA_long"] = data["Adj Close"].ewm(span=long_ma).mean()

            # Check if the MA_short crossed the MA_long bullish on the last day
            if direction == 'bullish':
                try:
                    if data["MA_short"][-1] > data["MA_long"][-1] and data["MA_short"][-2] < data["MA_long"][-2]:
                        # Print the ticker and the date of the crossover
                        st.write(f"{ticker} had a bullish crossover on {data.index[-1].date()}")
                        counter += 1
                        if universe != "S&P 500" and universe != "NASDAQ100":
                            chart_data = go.Candlestick(x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name=ticker, increasing_line_color="green", increasing_fillcolor="green", decreasing_line_color="red", decreasing_fillcolor="red")
                            fig = go.Figure(data=[chart_data])
                            ema_trace_short = go.Scatter(x=data.index, y=data["MA_short"], mode='lines', name='EMA short', marker_color="blue")
                            fig.add_trace(ema_trace_short)
                            ema_trace_long = go.Scatter(x=data.index, y=data["MA_long"], mode='lines', name='EMA long', marker_color="green")
                            fig.add_trace(ema_trace_long)                    
                            fig.update_layout(
                                title=ticker,
                                xaxis_tickfont_size=12,
                                yaxis=dict(
                                title='Price ($/share)',
                                titlefont_size=14,
                                tickfont_size=12,
                            ),
                            autosize=False,
                            width=800,
                            height=600,
                            margin=dict(l=50, r=50, b=100, t=100, pad=4),
                            paper_bgcolor='slategray', plot_bgcolor="lightgray"
                            )
                            st.plotly_chart(fig, use_container_width=True)     

                        else:
                            st.image(f"https://charts2-node.finviz.com/chart.ashx?cs=&t={ticker}&tf=d&s=linear&ct=candle_stick&r=&o[0][ot]=ema&o[0][op]={short_ma}&o[0][oc]=FF8F33C6&o[1][ot]=ema&o[1][op]={long_ma}&o[1][oc]=DCB3326D&o[2][ot]=patterns&o[2][op]=&o[2][oc]=000", width=700)
                        
                except Exception:
                    print("No data on " + ticker)
            else:
                try:
                    if data["MA_short"][-1] < data["MA_long"][-1] and data["MA_short"][-2] > data["MA_long"][-2]:
                        # Print the ticker and the date of the crossover
                        st.write(f"{ticker} had a bearish crossover on {data.index[-1].date()}")
                        counter += 1
                        if universe != "S&P 500" and universe != "NASDAQ100":
                            chart_data = go.Candlestick(x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name=ticker, increasing_line_color="green", increasing_fillcolor="green", decreasing_line_color="red", decreasing_fillcolor="red")
                            fig = go.Figure(data=[chart_data])
                            ema_trace_short = go.Scatter(x=data.index, y=data["MA_short"], mode='lines', name='EMA short', marker_color="blue")
                            fig.add_trace(ema_trace_short)
                            ema_trace_long = go.Scatter(x=data.index, y=data["MA_long"], mode='lines', name='EMA long', marker_color="green")
                            fig.add_trace(ema_trace_long)                    
                            fig.update_layout(
                                title=ticker,
                                xaxis_tickfont_size=12,
                                yaxis=dict(
                                title='Price ($/share)',
                                titlefont_size=14,
                                tickfont_size=12,
                            ),
                            autosize=False,
                            width=700,
                            height=600,
                            margin=dict(l=50, r=50, b=100, t=100, pad=4),
                            paper_bgcolor='slategray', plot_bgcolor="lightgray"
                            )
                            st.plotly_chart(fig, use_container_width=True)     
                        else:
                            st.image(f"https://charts2-node.finviz.com/chart.ashx?cs=&t={ticker}&tf=d&s=linear&ct=candle_stick&r=&o[0][ot]=ema&o[0][op]={short_ma}&o[0][oc]=FF8F33C6&o[1][ot]=ema&o[1][op]={long_ma}&o[1][oc]=DCB3326D&o[2][ot]=patterns&o[2][op]=&o[2][oc]=000", width=700)
                except Exception:
                    print("No data on " + ticker)
        st.write("Finished screening. Found " + str(counter) + " stock(s)")
st.sidebar.write('<span style="font-size: 12px;">(Fetching dynamic charts from finviz for US Stocks, plotting DAX Stocks)</span>', unsafe_allow_html=True)

