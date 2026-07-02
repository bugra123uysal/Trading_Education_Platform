"""
Grafik Oynatıcı (Replay) — TradingView'ın Bar Replay özelliğinin basit hali.

Mantık: kullanıcı bir hisse ve geçmişte bir başlangıç tarihi seçer;
grafik o tarihe "geri sarılır". Sonra oynat/adımla kontrolleriyle
mumlar gün gün ekrana gelir — gelecek gizlidir, kullanıcı fiyatın
nasıl aktığını gerçek zamanlı yaşar gibi izler. Bu, grafik okumayı
öğrenmenin en etkili yollarından biridir: "sonrasını bilmeden"
düşünme alışkanlığı kazandırır.

Streamlit'te animasyon: st.empty() içine döngüyle yeni grafik çizip
time.sleep ile bekliyoruz. Döngü sürerken buton tıklamaları işlenmez;
bu yüzden oynatma "seçilen kare sayısı kadar" çalışıp durur — kullanıcı
istediği an tekrar Oynat'a basar ya da adım butonlarıyla ilerler.
"""
import time

import streamlit as st

from app.database import session_scope
from app.data.fetcher import get_candles, DEFAULT_SYMBOLS
from ui.common import indicator_figure


SPEED_OPTIONS = {
    "Yavaş (0.5 sn/gün)": 0.5,
    "Normal (0.25 sn/gün)": 0.25,
    "Hızlı (0.1 sn/gün)": 0.1,
}


def render():
    st.title("Grafik Oynatıcı (Replay)")
    st.write(
        "Grafiği geçmişte bir tarihe geri sar, sonra gün gün oynat — geleceği "
        "bilmeden fiyatın nasıl aktığını izle. TradingView'daki Bar Replay'in "
        "eğitim amaçlı basit halidir."
    )

    symbol = st.selectbox(
        "Hisse Sembolü",
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
        key="rp_symbol",
    )

    # Veriyi yükle
    with st.spinner(f"{symbol} verisi yükleniyor…"):
        try:
            with session_scope() as db:
                bars = get_candles(db, symbol)
        except ValueError as e:
            st.error(str(e))
            return

    full_bars = [
        {"date": b.date, "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume}
        for b in bars
    ]
    dates = [b["date"] for b in full_bars]

    # Sembol değişince replay durumunu sıfırla
    if st.session_state.get("rp_active_symbol") != symbol:
        st.session_state.rp_active_symbol = symbol
        st.session_state.rp_index = None

    # --- Geri sarma noktası seçimi ---
    # En az 60 bar geçmiş kalsın ki grafik anlamlı görünsün
    min_idx = min(60, len(dates) - 2)
    start_date = st.select_slider(
        "Grafiği bu tarihe geri sar:",
        options=dates[min_idx:-1],
        value=dates[len(dates) // 2],
        key="rp_start_date",
    )
    start_idx = dates.index(start_date)

    c1, c2 = st.columns([1, 2])
    if c1.button("⏮ Bu Tarihe Geri Sar", use_container_width=True):
        st.session_state.rp_index = start_idx
    speed_label = c2.selectbox("Oynatma Hızı", options=list(SPEED_OPTIONS.keys()), index=1, key="rp_speed")
    speed = SPEED_OPTIONS[speed_label]

    if st.session_state.get("rp_index") is None:
        st.info("Yukarıdan bir tarih seçip 'Geri Sar' butonuna bas — grafik o güne dönecek.")
        return

    idx = st.session_state.rp_index
    idx = max(min_idx, min(idx, len(dates) - 1))
    current_date = dates[idx]
    remaining = len(dates) - 1 - idx

    # --- Kontroller ---
    k1, k2, k3, k4, k5 = st.columns(5)
    step1 = k1.button("+1 gün", use_container_width=True)
    step5 = k2.button("+5 gün", use_container_width=True)
    play20 = k3.button("▶ 20 gün oynat", use_container_width=True)
    play_all = k4.button("▶▶ Sona kadar", use_container_width=True)
    reset = k5.button("⏮ Başa dön", use_container_width=True)

    if reset:
        st.session_state.rp_index = start_idx
        st.rerun()
    if step1:
        st.session_state.rp_index = min(idx + 1, len(dates) - 1)
        st.rerun()
    if step5:
        st.session_state.rp_index = min(idx + 5, len(dates) - 1)
        st.rerun()

    # --- Durum bilgisi ---
    replay_start_price = full_bars[start_idx]["close"]
    current_price = full_bars[idx]["close"]
    change_pct = round((current_price - replay_start_price) / replay_start_price * 100, 2)
    m1, m2, m3 = st.columns(3)
    m1.metric("Şu Anki Tarih", current_date)
    m2.metric("Kapanış", f"${current_price}", f"{change_pct}% (geri sarma noktasından beri)")
    m3.metric("Kalan Gün", remaining)

    chart_slot = st.empty()

    def draw(upto_idx: int):
        chart_slot.plotly_chart(
            indicator_figure(
                full_bars[: upto_idx + 1],
                display_start=dates[max(0, upto_idx - 120)],  # son ~120 gün görünür, TradingView hissi
                vline_date=start_date,
                vline_label="Geri sarma noktası",
            ),
            use_container_width=True,
            key=f"rp_chart_{upto_idx}_{time.time_ns()}",
        )

    # --- Oynatma ---
    if play20 or play_all:
        frames = remaining if play_all else min(20, remaining)
        if frames == 0:
            st.warning("Grafik zaten en güncel tarihte — oynatılacak gün kalmadı.")
            draw(idx)
        else:
            for i in range(1, frames + 1):
                draw(idx + i)
                time.sleep(speed)
            st.session_state.rp_index = idx + frames
            st.success(
                f"{frames} gün oynatıldı. Şu an {dates[idx + frames]} tarihindesin. "
                "Devam etmek için tekrar oynat ya da adım butonlarını kullan."
            )
    else:
        draw(idx)

    st.caption(
        "İpucu: Bir tarihte dur, kendine 'buradan sonra ne olur?' diye sor, tahminini "
        "yap, sonra oynat ve gerçekle karşılaştır. Bu alıştırmayı farklı hisse ve "
        "dönemlerde tekrarlamak, grafik okuma refleksini geliştirir."
    )
