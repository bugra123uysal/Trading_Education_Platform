import streamlit as st

from app.data.fetcher import DEFAULT_SYMBOLS, DATA_UNAVAILABLE_MESSAGE
from ui.common import candlestick_figure, load_candles


def render():
    st.title("Hisse Senedi Grafikleri")
    st.write("Gerçek geçmiş veriler üzerinde mum grafiklerini inceleyin.")

    symbol = st.selectbox(
        "Hisse Sembolü",
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
    )

    with st.spinner(f"{symbol} verisi yükleniyor…"):
        candles = load_candles(symbol)

    if not candles:
        st.warning(DATA_UNAVAILABLE_MESSAGE)
        return

    st.plotly_chart(candlestick_figure(candles), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    last = candles[-1]
    first = candles[0]
    change_pct = round((last["close"] - first["close"]) / first["close"] * 100, 2)
    col1.metric("Son Kapanış", f"${last['close']}")
    col2.metric("Toplam Değişim (gösterilen aralıkta)", f"{change_pct}%")
    col3.metric("Bar Sayısı", len(candles))
