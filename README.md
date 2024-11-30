# ETH vs Bitcoin Price <!-- omit in toc -->

This repo provides an interactive way to compare the returns of $ETH and $BTC
over different time periods.

You can access it at [ethvsbitcoin.streamlit.app/](https://ethvsbitcoin.streamlit.app/).

## Demo

![demo](https://github.com/user-attachments/assets/b4e4b23c-065b-4bbe-bcf4-f696239f95ba)

## QuickStart (Running this yourself)

```bash
make env_create
$(make env_source)
make pip_install
make run
```

## Why?

I saw [this tweet](https://x.com/dsiroker/status/1858953933244559526) and realized
that we all use the default tools provided by Google that only provide a quick and
easy way to compare the "last X time period".

I wanted to have an easy interactive way to compare the returns by varying both
the start and end times side by side.

![demo](https://github.com/user-attachments/assets/51cf1768-737f-4479-8418-a37b974e67fe)

## TODO

### Interactive Range Slider

Updating the range slider in the plot doesn't update the whole page.

I tried to make the slider interactive using both [Streamlit's Plotly events](https://github.com/streamlit/streamlit/issues/455#issuecomment-2111149108) and the OSS [streamlit-plotly-events](https://github.com/ethanhe42/streamlit-plotly-events) but haven't succeeded with either one (yet)."""

---

## License

This project is licensed under the MIT License; see the [LICENSE](https://github.com/pokt-network/poktroll/blob/main/LICENSE) file for details.
