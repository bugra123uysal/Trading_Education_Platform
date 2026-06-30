from datetime import date

import pandas as pd
import streamlit as st

from app.database import session_scope
from app.data.fetcher import get_candles, DEFAULT_SYMBOLS
from app.backtest.engine import run_backtest
from ui.common import indicator_figure, term_expander

STRATEGY_LABELS = {
    "ma_crossover": "Hareketli Ortalama Kesişimi",
    "rsi_threshold": "RSI Eşik Değeri",
}


def render():
    st.title("Backtest Motoru")
    st.write(
        "Bir strateji seçip geçmiş veri üzerinde nasıl performans gösterdiğini görün. "
        "Backtest, bir stratejiyi gerçek parayla denemeden önce geçmişte nasıl "
        "çalışacağını test etme yöntemidir."
    )
    term_expander("backtest", label_prefix="Bu terimi merak ediyorsan")

    col_symbol, col_strategy = st.columns(2)
    symbol = col_symbol.selectbox(
        "Hisse Sembolü",
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
    )
    strategy = col_strategy.selectbox(
        "Strateji", options=list(STRATEGY_LABELS.keys()), format_func=lambda s: STRATEGY_LABELS[s]
    )

    with st.form("backtest_form"):
        col1, col2, col3 = st.columns(3)
        start_date = col1.date_input("Başlangıç Tarihi", value=date(2023, 1, 1))
        end_date = col2.date_input("Bitiş Tarihi", value=date.today())
        initial_capital = col3.number_input("Başlangıç Sermayesi ($)", value=10000, min_value=100, step=100)

        params = {}
        if strategy == "ma_crossover":
            c1, c2 = st.columns(2)
            params["fast_period"] = c1.number_input("Kısa Ortalama (gün)", value=20, min_value=2)
            params["slow_period"] = c2.number_input("Uzun Ortalama (gün)", value=50, min_value=3)
        else:
            c1, c2, c3 = st.columns(3)
            params["rsi_period"] = c1.number_input("RSI Periyodu", value=14, min_value=2)
            params["buy_below"] = c2.number_input("Alış Eşiği (altında)", value=30, min_value=1, max_value=50)
            params["sell_above"] = c3.number_input("Satış Eşiği (üstünde)", value=70, min_value=50, max_value=99)

        submitted = st.form_submit_button("Backtest Çalıştır")

    if not submitted:
        return

    with st.spinner("Backtest çalışıyor…"):
        try:
            with session_scope() as db:
                bars = get_candles(db, symbol)
        except ValueError as e:
            st.error(str(e))
            return

        start_str, end_str = start_date.isoformat(), end_date.isoformat()
        full_bars = [
            {"date": b.date, "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
            for b in bars
        ]
        filtered = [b for b in full_bars if start_str <= b["date"] <= end_str]
        if not filtered:
            st.error("Seçilen tarih aralığında veri bulunamadı.")
            return

        try:
            result = run_backtest(filtered, strategy, initial_capital=initial_capital, **params)
        except ValueError as e:
            st.error(str(e))
            return

    st.subheader(f"{symbol} — {STRATEGY_LABELS[strategy]}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Getiri", f"{result['total_return_pct']}%")
    m2.metric("Son Sermaye", f"${result['final_capital']:,.2f}")
    m3.metric("İşlem Sayısı", result["total_trades"])
    m4.metric("Kazanma Oranı", f"{result['win_rate']}%")

    if result["best_trade"]:
        b1, b2 = st.columns(2)
        bt, wt = result["best_trade"], result["worst_trade"]
        b1.metric("En İyi İşlem", f"+{bt['profit_pct']}%", f"{bt['entry_date']} → {bt['exit_date']}")
        b2.metric("En Kötü İşlem", f"{wt['profit_pct']}%", f"{wt['entry_date']} → {wt['exit_date']}")
    else:
        st.info("Bu strateji ve tarih aralığında hiç işlem yapılmadı.")

    markers = []
    for t in result["trades"]:
        markers.append({"date": t["entry_date"], "color": "#3fb27f"})
        markers.append({"date": t["exit_date"], "color": "#d9534f"})
    st.plotly_chart(
        indicator_figure(full_bars, display_start=start_str, display_end=end_str, markers=markers),
        use_container_width=True,
    )

    if result["trades"]:
        st.subheader("İşlem Geçmişi")
        df = pd.DataFrame(result["trades"])
        df = df.rename(columns={
            "entry_date": "Giriş", "entry_price": "Giriş Fiyatı",
            "exit_date": "Çıkış", "exit_price": "Çıkış Fiyatı",
            "profit_pct": "Getiri (%)", "profit_abs": "Kâr/Zarar ($)",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
