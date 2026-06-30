import streamlit as st

from app.database import session_scope
from app.data.fetcher import get_candles, DEFAULT_SYMBOLS
from ui.common import candlestick_figure


def render():
    st.title("Hisse Senedi Grafikleri")
    st.write("Gerçek geçmiş veriler üzerinde mum grafiklerini inceleyin.")

    symbol = st.selectbox(
        "Hisse Sembolü",
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
    )

    with st.spinner(f"{symbol} verisi yükleniyor…"):
        try:
            with session_scope() as db:
                bars = get_candles(db, symbol)
        except ValueError as e:
            st.error(str(e))
            return

    candles = [
        {"date": b.date, "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
        for b in bars
    ]

    st.plotly_chart(candlestick_figure(candles), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    last = candles[-1]
    first = candles[0]
    change_pct = round((last["close"] - first["close"]) / first["close"] * 100, 2)
    col1.metric("Son Kapanış", f"${last['close']}")
    col2.metric("Toplam Değişim (gösterilen aralıkta)", f"{change_pct}%")
    col3.metric("Bar Sayısı", len(candles))
