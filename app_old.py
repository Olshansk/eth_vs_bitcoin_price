from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf


# Fetch data
def get_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    data["Return"] = data["Close"].pct_change().cumsum() * 100
    return data


# App setup
st.title("ETH vs BTC Return Comparison")

# Set default dates
today = datetime.today()
one_year_ago = today - timedelta(days=365)

start_date = st.date_input("Start Date", value=one_year_ago)
end_date = st.date_input("End Date", value=today)

st.write(f"Selected Start Date: {start_date}")
st.write(f"Selected End Date: {end_date}")

# Fetch BTC and ETH data
btc = get_data("BTC-USD", start_date, end_date)
eth = get_data("ETH-USD", start_date, end_date)

# Select timeframe
st.write("Adjust the lens:")
lens_range = st.slider("Time Range", min_value=0, max_value=len(btc), value=(0, len(btc)), step=1)

# # Filter data
filtered_btc = btc.iloc[lens_range[0] : lens_range[1]]
filtered_eth = eth.iloc[lens_range[0] : lens_range[1]]


# Display returns
btc_return = filtered_btc["Return"].iloc[-1] if not filtered_btc.empty else 0
eth_return = filtered_eth["Return"].iloc[-1] if not filtered_eth.empty else 0
st.write(f"BTC Return: {btc_return:.2f}%")
st.write(f"ETH Return: {eth_return:.2f}%")


# Plot chart
fig = px.line(
    x=filtered_btc.index, y=filtered_btc["Close"].values.flatten(), labels={"y": "BTC Price"}, title="BTC vs ETH Prices"
)
fig.add_scatter(x=filtered_eth.index, y=filtered_eth["Close"].values.flatten(), mode="lines", name="ETH Price")
st.plotly_chart(fig)
