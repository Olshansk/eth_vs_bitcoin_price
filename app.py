from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


# Fetch data with caching
@st.cache_data
def get_data(symbol):
    data = yf.download(symbol, period="max")
    data.dropna(inplace=True)  # Remove rows with missing values
    data["Return"] = data["Close"].pct_change().cumsum() * 100
    data.index = pd.to_datetime(data.index)
    return data


# App setup
st.title("ETH vs BTC Return Comparison")

# Fetch BTC and ETH data
btc = get_data("BTC-USD")
eth = get_data("ETH-USD")

# Check if data is loaded
if btc.empty or eth.empty:
    st.error("Data not available.")
    st.stop()

# Display min and max dates for BTC and ETH
btc_min_date = btc.index.min().date()
btc_max_date = btc.index.max().date()
eth_min_date = eth.index.min().date()
eth_max_date = eth.index.max().date()


# Define date range for the slider based on overlapping dates
min_date = max(btc_min_date, eth_min_date)
max_date = min(btc_max_date, eth_max_date)

# Set default date range to the last year of data
default_end_date = max_date
default_start_date = default_end_date - timedelta(days=365)
if default_start_date < min_date:
    default_start_date = min_date

# Streamlit slider for date selection
start_date, end_date = st.slider(
    "Select Date Range:",
    min_value=min_date,
    max_value=max_date,
    value=(default_start_date, default_end_date),
    format="YYYY-MM-DD",
)

# Filter data based on Streamlit slider
btc_filtered = btc.loc[start_date:end_date]
eth_filtered = eth.loc[start_date:end_date]

# Calculate returns for the filtered range
btc_return = btc_filtered["Return"].iloc[-1] - btc_filtered["Return"].iloc[0]
eth_return = eth_filtered["Return"].iloc[-1] - eth_filtered["Return"].iloc[0]

# Determine colors based on returns
btc_color = "green" if btc_return >= 0 else "red"
eth_color = "green" if eth_return >= 0 else "red"

# Create formatted return texts
btc_return_text = f"## BTC Return: <b style='color:{btc_color};'>{btc_return:.2f}%</b>"
eth_return_text = f"## ETH Return: <b style='color:{eth_color};'>{eth_return:.2f}%</b>"


# Function to get heading level based on return magnitude
def get_heading_level(percentage):
    if abs(percentage) >= 100:
        return "#"
    elif abs(percentage) >= 50:
        return "##"
    elif abs(percentage) >= 10:
        return "###"
    else:
        return "####"


# Determine heading levels
btc_heading = get_heading_level(btc_return)
eth_heading = get_heading_level(eth_return)

# Create formatted return texts
btc_return_text = f"{btc_heading} BTC Return: <b style='color:{btc_color};'>{btc_return:.2f}%</b>"
eth_return_text = f"{eth_heading} ETH Return: <b style='color:{eth_color};'>{eth_return:.2f}%</b>"

# Display returns in order of magnitude (bigger return first)
if btc_return >= eth_return:
    st.markdown(btc_return_text, unsafe_allow_html=True)
    st.markdown(eth_return_text, unsafe_allow_html=True)
else:
    st.markdown(eth_return_text, unsafe_allow_html=True)
    st.markdown(btc_return_text, unsafe_allow_html=True)

# Create the figure
fig = go.Figure()

# Add BTC trace
fig.add_trace(go.Scatter(x=btc.index, y=btc["Close"].squeeze().tolist(), mode="lines", name="BTC Price"))

# Add ETH trace with secondary y-axis
fig.add_trace(go.Scatter(x=eth.index, y=eth["Close"].squeeze().tolist(), mode="lines", name="ETH Price", yaxis="y2"))

# Set up layout with secondary y-axis and range slider
fig.update_layout(
    yaxis=dict(title="BTC Price (USD)"),
    yaxis2=dict(title="ETH Price (USD)", overlaying="y", side="right"),
    xaxis=dict(
        title="Date",
        rangeslider=dict(visible=True),
        range=[start_date, end_date],  # Update range dynamically based on Streamlit slider
    ),
    title="BTC vs ETH Price Comparison",
    legend=dict(orientation="v", x=1.05, y=1),  # Move legend to the right-hand side
)

# Render the chart
st.plotly_chart(fig, use_container_width=True)

# Display the note prominently
st.warning(
    """
Updating the range slider in the plot doesn't update the whole page.

I tried to make the slider interactive using both [Streamlit's Plotly events](https://github.com/streamlit/streamlit/issues/455#issuecomment-2111149108) and the OSS [streamlit-plotly-events](https://github.com/ethanhe42/streamlit-plotly-events) but haven't succeeded with either one (yet)."""
)

st.write("---")
st.write(f"*BTC data available from `{btc_min_date}` to `{btc_max_date}`*")
st.write(f"*ETH data available from `{eth_min_date}` to `{eth_max_date}`*")
