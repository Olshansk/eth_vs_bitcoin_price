from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from pydantic import BaseModel, Field


class CryptoData(BaseModel):
    """Data model for cryptocurrency information."""

    symbol: str
    data: pd.DataFrame
    min_date: datetime
    max_date: datetime
    return_value: Optional[float] = None
    return_color: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True  # Allow pd.DataFrame


class ComparisonResult(BaseModel):
    """Results from comparing two cryptocurrencies."""

    start_date: datetime
    end_date: datetime
    src_asset: CryptoData
    compare_asset: CryptoData

    class Config:
        arbitrary_types_allowed = True


@st.cache_data
def get_crypto_data(symbol: str) -> CryptoData:
    """
    Fetch and process cryptocurrency data.

    Args:
        symbol: The cryptocurrency symbol (e.g., 'BTC', 'ETH')

    Returns:
        CryptoData object containing the processed data and metadata
    """
    data = yf.download(f"{symbol}-USD", period="max")
    data.dropna(inplace=True)
    data["Return"] = data["Close"].pct_change().cumsum() * 100
    data.index = pd.to_datetime(data.index)

    return CryptoData(symbol=symbol, data=data, min_date=data.index.min(), max_date=data.index.max())


def get_heading_level(percentage: float) -> str:
    """
    Determine markdown heading level based on return magnitude.

    Args:
        percentage: The return percentage value

    Returns:
        String representing the markdown heading level
    """
    if abs(percentage) >= 100:
        return "#"
    elif abs(percentage) >= 50:
        return "##"
    elif abs(percentage) >= 10:
        return "###"
    return "####"


def compare_crypto_assets(src_asset: str, compare_asset: str, default_days: int = 365) -> ComparisonResult:
    """
    Compare two cryptocurrency assets and prepare visualization data.

    Args:
        src_asset: Source asset symbol (e.g., 'BTC')
        compare_asset: Comparison asset symbol (e.g., 'ETH')
        default_days: Default number of days for the comparison period

    Returns:
        ComparisonResult object containing processed comparison data
    """
    # Fetch data for both assets
    src_data = get_crypto_data(src_asset)
    compare_data = get_crypto_data(compare_asset)

    # Define date range based on overlapping dates
    min_date = max(src_data.min_date, compare_data.min_date)
    max_date = min(src_data.max_date, compare_data.max_date)

    # Set default date range
    default_end_date = max_date
    default_start_date = default_end_date - timedelta(days=default_days)
    if default_start_date < min_date:
        default_start_date = min_date

    # Create date selector
    start_date, end_date = st.slider(
        "Select Date Range:",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=(default_start_date.date(), default_end_date.date()),
        format="YYYY-MM-DD",
    )

    # Filter data and calculate returns
    for asset in [src_data, compare_data]:
        filtered_data = asset.data.loc[start_date:end_date]
        asset.return_value = filtered_data["Return"].iloc[-1] - filtered_data["Return"].iloc[0]
        asset.return_color = "green" if asset.return_value >= 0 else "red"

    return ComparisonResult(
        start_date=pd.Timestamp(start_date),
        end_date=pd.Timestamp(end_date),
        src_asset=src_data,
        compare_asset=compare_data,
    )


def display_comparison(result: ComparisonResult) -> None:
    """
    Display the cryptocurrency comparison results.

    Args:
        result: ComparisonResult object containing the comparison data
    """
    # Display returns
    for asset in sorted(
        [result.src_asset, result.compare_asset],
        key=lambda x: x.return_value or 0,
        reverse=True,
    ):
        heading = get_heading_level(asset.return_value or 0)
        return_text = (
            f"{heading} {asset.symbol} Return: " f"<b style='color:{asset.return_color};'>{asset.return_value:.2f}%</b>"
        )
        st.markdown(return_text, unsafe_allow_html=True)

    # Create price comparison chart
    fig = go.Figure()

    # Add source asset trace
    fig.add_trace(
        go.Scatter(
            x=result.src_asset.data.index,
            y=result.src_asset.data["Close"].squeeze().tolist(),
            mode="lines",
            name=f"{result.src_asset.symbol} Price",
        )
    )

    # Add comparison asset trace
    fig.add_trace(
        go.Scatter(
            x=result.compare_asset.data.index,
            y=result.compare_asset.data["Close"].squeeze().tolist(),
            mode="lines",
            name=f"{result.compare_asset.symbol} Price",
            yaxis="y2",
        )
    )

    # Configure layout
    fig.update_layout(
        yaxis=dict(title=f"{result.src_asset.symbol} Price (USD)"),
        yaxis2=dict(
            title=f"{result.compare_asset.symbol} Price (USD)",
            overlaying="y",
            side="right",
        ),
        xaxis=dict(
            title="Date",
            rangeslider=dict(visible=True),
            range=[result.start_date, result.end_date],
        ),
        title=f"{result.src_asset.symbol} vs {result.compare_asset.symbol} Price Comparison",
        legend=dict(orientation="v", x=1.05, y=1),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.warning(
        """
        ⚠️ Updating the range slider in the plot doesn't update the whole page. ⚠️

        I tried to make the slider interactive using both
        [Streamlit's Plotly events](https://github.com/streamlit/streamlit/issues/455#issuecomment-2111149108)
        and the OSS [streamlit-plotly-events](https://github.com/ethanhe42/streamlit-plotly-events)
        but haven't succeeded with either one (yet).
        """
    )

    # Display data availability info
    st.write("---")
    for asset in [result.src_asset, result.compare_asset]:
        st.write(f"*{asset.symbol} data available from " f"`{asset.min_date.date()}` to `{asset.max_date.date()}`*")


def main():
    """Main application entry point."""
    st.title("Crypto Return Comparison")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["BTC vs ETH", "BTC vs SOL", "ETH vs SOL"])

    with tab1:
        result = compare_crypto_assets("BTC", "ETH")
        display_comparison(result)

    with tab2:
        st.info("BTC vs SOL comparison coming soon!")

    with tab3:
        st.info("ETH vs SOL comparison coming soon!")


if __name__ == "__main__":
    main()
