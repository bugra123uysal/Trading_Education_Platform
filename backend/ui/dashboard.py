import streamlit as st

from app.data.fetcher import DEFAULT_SYMBOLS
from app.i18n import t
from ui.common import candlestick_figure, load_candles


def render():
    st.title(t("dash_title"))
    st.write(t("dash_intro"))

    symbol = st.selectbox(
        t("symbol_label"),
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
    )

    with st.spinner(t("loading", symbol=symbol)):
        candles = load_candles(symbol)

    if not candles:
        st.warning(t("data_unavailable"))
        return

    st.plotly_chart(candlestick_figure(candles), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    last = candles[-1]
    first = candles[0]
    change_pct = round((last["close"] - first["close"]) / first["close"] * 100, 2)
    col1.metric(t("dash_last_close"), f"${last['close']}")
    col2.metric(t("dash_total_change"), f"{change_pct}%")
    col3.metric(t("dash_bar_count"), len(candles))
