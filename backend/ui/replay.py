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

from app.data.fetcher import DEFAULT_SYMBOLS
from app.i18n import t
from ui.common import indicator_figure, load_candles

# Etiket -> saniye. Etiketler t() ile üretilir (dile göre değişir).
SPEED_SECONDS = {"slow": 0.5, "normal": 0.25, "fast": 0.1}


def render():
    st.title(t("replay_title"))
    st.write(t("replay_intro"))

    symbol = st.selectbox(
        t("symbol_label"),
        options=list(DEFAULT_SYMBOLS.keys()),
        format_func=lambda s: f"{s} — {DEFAULT_SYMBOLS[s]}",
        key="rp_symbol",
    )

    with st.spinner(t("loading", symbol=symbol)):
        full_bars = load_candles(symbol)

    if not full_bars:
        st.warning(t("data_unavailable"))
        return

    dates = [b["date"] for b in full_bars]

    # Sembol değişince replay durumunu sıfırla
    if st.session_state.get("rp_active_symbol") != symbol:
        st.session_state.rp_active_symbol = symbol
        st.session_state.rp_index = None

    # --- Geri sarma noktası seçimi ---
    # En az 60 bar geçmiş kalsın ki grafik anlamlı görünsün
    min_idx = min(60, len(dates) - 2)
    start_date = st.select_slider(
        t("replay_rewind_to"),
        options=dates[min_idx:-1],
        value=dates[len(dates) // 2],
        key="rp_start_date",
    )
    start_idx = dates.index(start_date)

    speed_labels = {
        "slow": t("replay_speed_slow"),
        "normal": t("replay_speed_normal"),
        "fast": t("replay_speed_fast"),
    }
    c1, c2 = st.columns([1, 2])
    if c1.button(t("replay_rewind_btn"), use_container_width=True):
        st.session_state.rp_index = start_idx
    speed_code = c2.selectbox(
        t("replay_speed"),
        options=list(SPEED_SECONDS.keys()),
        index=1,
        format_func=lambda c: speed_labels[c],
        key="rp_speed",
    )
    speed = SPEED_SECONDS[speed_code]

    if st.session_state.get("rp_index") is None:
        st.info(t("replay_hint_start"))
        return

    idx = st.session_state.rp_index
    idx = max(min_idx, min(idx, len(dates) - 1))
    current_date = dates[idx]
    remaining = len(dates) - 1 - idx

    # --- Kontroller ---
    k1, k2, k3, k4, k5 = st.columns(5)
    step1 = k1.button(t("replay_step1"), use_container_width=True)
    step5 = k2.button(t("replay_step5"), use_container_width=True)
    play20 = k3.button(t("replay_play20"), use_container_width=True)
    play_all = k4.button(t("replay_play_all"), use_container_width=True)
    reset = k5.button(t("replay_reset"), use_container_width=True)

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
    m1.metric(t("replay_current_date"), current_date)
    m2.metric(t("replay_close"), f"${current_price}", t("replay_change_since", pct=change_pct))
    m3.metric(t("replay_days_left"), remaining)

    chart_slot = st.empty()

    def draw(upto_idx: int):
        chart_slot.plotly_chart(
            indicator_figure(
                full_bars[: upto_idx + 1],
                display_start=dates[max(0, upto_idx - 120)],  # son ~120 gün görünür, TradingView hissi
                vline_date=start_date,
                vline_label=t("replay_rewind_point"),
            ),
            use_container_width=True,
            key=f"rp_chart_{upto_idx}_{time.time_ns()}",
        )

    # --- Oynatma ---
    if play20 or play_all:
        frames = remaining if play_all else min(20, remaining)
        if frames == 0:
            st.warning(t("replay_no_days"))
            draw(idx)
        else:
            for i in range(1, frames + 1):
                draw(idx + i)
                time.sleep(speed)
            st.session_state.rp_index = idx + frames
            st.success(t("replay_played", n=frames, date=dates[idx + frames]))
    else:
        draw(idx)

    st.caption(t("replay_tip"))
