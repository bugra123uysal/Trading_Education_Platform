"""
Sayfalar arasında paylaşılan yardımcı fonksiyonlar.

Streamlit, kullanıcı her etkileşimde tüm script'i baştan çalıştırır.
Bu yüzden "tıklanabilir terim" mantığını JS popup yerine basit bir
st.expander ile çözüyoruz: kullanıcı terimin üzerine tıklayıp açıyor,
tekrar tıklayıp kapatıyor — Streamlit'in kendi native bileşeni, ekstra
JS/HTML hack'ine gerek yok.
"""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.database import session_scope
from app.data.fetcher import CACHE_TTL, get_candles
from app.indicators import with_indicators
from app.models import GlossaryTerm

CATEGORY_LABELS = {
    "temel": "Temel Kavram",
    "teknik-analiz": "Teknik Analiz",
    "risk-yonetimi": "Risk Yönetimi",
}


@st.cache_data(ttl=int(CACHE_TTL.total_seconds()))
def load_candles(symbol: str) -> list[dict] | None:
    """Sembolün mumlarını düz dict listesi olarak döndürür (veya hata durumunda None).

    SQLite cache'inin üstüne süreç-içi bir @st.cache_data katmanı ekler:
    aynı sembol arka arkaya istendiğinde DB'ye bile gidilmez. ORM nesnesi
    değil düz dict cache'lenir — böylece oturum kapansa da veri güvenli
    kalır (detached instance sorunu olmaz). TTL, SQLite katmanıyla tutarlı.
    """
    try:
        with session_scope() as db:
            bars = get_candles(db, symbol)
    except ValueError:
        return None
    return [
        {"date": b.date, "open": b.open, "high": b.high,
         "low": b.low, "close": b.close, "volume": b.volume}
        for b in bars
    ]


def term_expander(slug: str, label_prefix: str = "Terim") -> None:
    """Verilen slug'a ait terimi st.expander içinde gösterir."""
    with session_scope() as db:
        term = db.query(GlossaryTerm).filter(GlossaryTerm.slug == slug).first()
    if term is None:
        return
    with st.expander(f"{label_prefix}: {term.term}"):
        st.caption(CATEGORY_LABELS.get(term.category, term.category))
        st.write(term.child_explanation)
        if term.example:
            st.info(term.example)


def candlestick_figure(candles: list[dict], markers: list[dict] | None = None) -> go.Figure:
    """
    candles: [{date, open, high, low, close}, ...]
    markers: [{date, text, color, symbol, position}, ...] (opsiyonel, alım/satım işaretleri için)
    """
    dates = [c["date"] for c in candles]
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=dates,
                open=[c["open"] for c in candles],
                high=[c["high"] for c in candles],
                low=[c["low"] for c in candles],
                close=[c["close"] for c in candles],
                increasing_line_color="#3fb27f",
                decreasing_line_color="#d9534f",
                increasing_fillcolor="#3fb27f",
                decreasing_fillcolor="#d9534f",
                name="Fiyat",
            )
        ]
    )

    if markers:
        close_by_date = {c["date"]: c["close"] for c in candles}
        for group_color, group_symbol, group_name in [
            ("#3fb27f", "triangle-up", "Alış"),
            ("#d9534f", "triangle-down", "Satış"),
        ]:
            group = [m for m in markers if m["color"] == group_color]
            if not group:
                continue
            fig.add_trace(
                go.Scatter(
                    x=[m["date"] for m in group],
                    y=[close_by_date.get(m["date"]) for m in group],
                    mode="markers",
                    marker=dict(symbol=group_symbol, size=12, color=group_color),
                    name=group_name,
                )
            )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        height=460,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=1.02),
    )
    return fig


def indicator_figure(
    full_bars: list[dict],
    display_start: str | None = None,
    display_end: str | None = None,
    markers: list[dict] | None = None,
    vline_date: str | None = None,
    vline_label: str | None = None,
) -> go.Figure:
    """
    Hisseyle ilgili tek grafik: üstte fiyat + 3 EMA (50/100/200), altta
    Dolar Hacmi + 50 günlük ortalaması. İndikatörler `full_bars`'ın
    tamamı (warm-up için gereken geçmiş dahil) üzerinden hesaplanır,
    sonra sadece `display_start`/`display_end` aralığı gösterilir —
    aksi halde EMA'lar pencerenin başında yanlış/eksik çıkar.

    full_bars: [{date, open, high, low, close, volume}, ...]
    markers: [{date, color}, ...] — backtest alış/satış noktaları için
    vline_date: bu tarihte dikey kesikli çizgi çizilir (örn. senaryoda
    "işleme girdiğin an" ile sonrasını ayırmak için)
    """
    df = with_indicators(full_bars)
    if display_start:
        df = df[df["date"] >= display_start]
    if display_end:
        df = df[df["date"] <= display_end]
    df = df.reset_index(drop=True)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.04,
        subplot_titles=("Fiyat + 3 EMA (50 / 100 / 200)", "Dolar Hacmi (Qullamaggie Style)"),
    )

    fig.add_trace(
        go.Candlestick(
            x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
            increasing_line_color="#3fb27f", decreasing_line_color="#d9534f",
            increasing_fillcolor="#3fb27f", decreasing_fillcolor="#d9534f",
            name="Fiyat",
        ),
        row=1, col=1,
    )
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema_50"], line=dict(color="red", width=1), name="EMA 50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema_100"], line=dict(color="red", width=2), name="EMA 100"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema_200"], line=dict(color="red", width=3), name="EMA 200"), row=1, col=1)

    if markers:
        close_by_date = dict(zip(df["date"], df["close"]))
        for group_color, group_symbol, group_name in [
            ("#3fb27f", "triangle-up", "Alış"),
            ("#d9534f", "triangle-down", "Satış"),
        ]:
            group = [m for m in markers if m["color"] == group_color]
            if not group:
                continue
            fig.add_trace(
                go.Scatter(
                    x=[m["date"] for m in group],
                    y=[close_by_date.get(m["date"]) for m in group],
                    mode="markers",
                    marker=dict(symbol=group_symbol, size=12, color=group_color),
                    name=group_name,
                ),
                row=1, col=1,
            )

    fig.add_trace(
        go.Bar(x=df["date"], y=df["dollar_volume"], marker_color="rgba(31,119,180,0.45)", name="Dolar Hacmi"),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["dollar_volume_ma50"], line=dict(color="orange", width=2), name="50 MA"),
        row=2, col=1,
    )

    if vline_date:
        # İki alt grafiğe de aynı dikey kesikli çizgiyi çiz — "işlem anı"
        # ile sonrasını görsel olarak ayırır.
        for row in (1, 2):
            fig.add_vline(
                x=vline_date, line_dash="dash", line_color="#d9a441", line_width=2,
                row=row, col=1,
            )
        if vline_label:
            fig.add_annotation(
                x=vline_date, y=1.0, yref="paper",
                text=vline_label, showarrow=False,
                font=dict(color="#d9a441", size=12),
                bgcolor="rgba(11,15,23,0.7)",
                xanchor="left",
            )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        height=620,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", y=1.06),
    )
    return fig
