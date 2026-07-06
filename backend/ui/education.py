"""
Teknik Analiz Eğitimi sayfası.

Her ders: kavramın sade anlatımı + GERÇEK hisse grafiği üzerinde,
gerçek tarihlerle işaretlenmiş örnekler. İşaretlerin hepsi
app/analysis.py'deki tespit fonksiyonlarıyla veriden bulunur —
"bu olay bu tarihte gerçekten oldu" garantisi budur.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.database import session_scope
from app.data.fetcher import get_candles
from app import analysis
from ui.common import term_expander

PATTERN_TR = {
    "doji": "Doji",
    "hammer": "Çekiç (Hammer)",
    "shooting_star": "Kayan Yıldız (Shooting Star)",
    "bullish_engulfing": "Yutan Boğa (Bullish Engulfing)",
    "bearish_engulfing": "Yutan Ayı (Bearish Engulfing)",
}


@st.cache_data(ttl=3600)
def _load_df(symbol: str) -> pd.DataFrame:
    with session_scope() as db:
        bars = get_candles(db, symbol)
    return pd.DataFrame(
        [{"date": b.date, "open": b.open, "high": b.high, "low": b.low,
          "close": b.close, "volume": b.volume} for b in bars]
    )


def _candles(fig, df, row=None):
    trace = go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#3fb27f", decreasing_line_color="#d9534f",
        increasing_fillcolor="#3fb27f", decreasing_fillcolor="#d9534f", name="Fiyat",
    )
    # row/col sadece make_subplots ile oluşturulmuş figürlerde geçerli
    if row is None:
        fig.add_trace(trace)
    else:
        fig.add_trace(trace, row=row, col=1)


def _layout(fig, height=520):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False, height=height,
        margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.05),
    )
    return fig


def _annotate(fig, date, price, text, color="#d9a441", ay=-40):
    fig.add_annotation(
        x=date, y=price, text=text, showarrow=True, arrowhead=2, ay=ay,
        font=dict(color=color, size=11), arrowcolor=color, bgcolor="rgba(11,15,23,0.8)",
    )


def render():
    st.title("Teknik Analiz Eğitimi")
    st.write(
        "Her ders, kavramı önce sade bir dille anlatır; sonra **gerçek bir hisse "
        "grafiğinde, gerçek tarihiyle** örneğini gösterir. Grafiklerdeki tüm işaretler "
        "geçmiş veriden otomatik tespit edilmiştir — kurgu örnek yoktur. "
        "Öğrendiklerini Quiz sayfasındaki **Grafik Okuma** testiyle sınayabilirsin."
    )

    lessons = {
        "1. Trend ve Piyasa Yapısı (HH/HL)": _lesson_trend,
        "2. Destek ve Direnç": _lesson_support_resistance,
        "3. Mum Formasyonları": _lesson_candles,
        "4. Hareketli Ortalamalar ve Altın Kesişim": _lesson_ma,
        "5. RSI ile Momentum": _lesson_rsi,
        "6. Bollinger Bantları ve Volatilite": _lesson_bollinger,
        "7. Hacim Analizi: Teyit ve Kuruma": _lesson_volume,
        "8. Gap (Boşluk) Türleri": _lesson_gaps,
        "9. Fibonacci Düzeltmeleri": _lesson_fibonacci,
        "10. Risk Yönetimi: Stop, Hedef, R:R": _lesson_risk,
        "11. Qullamaggie Swing Stratejisi (3 Setup)": _lesson_qullamaggie,
    }
    choice = st.selectbox("Ders seç", options=list(lessons.keys()))
    st.divider()
    lessons[choice]()


# ---------- Dersler ----------

def _lesson_trend():
    st.subheader("Trend ve Piyasa Yapısı")
    st.markdown(
        "Fiyat üç yönde hareket eder: **yükselen trend**, **düşen trend**, **yatay**. "
        "Trendi tanımanın en sağlam yolu tepe ve dipleri izlemektir:\n\n"
        "- **HH (Higher High)**: bir önceki tepeden daha yüksek tepe → yükseliş sürüyor\n"
        "- **HL (Higher Low)**: bir önceki dipten daha yüksek dip → alıcılar erken davranıyor\n"
        "- **LH (Lower High)** ve **LL (Lower Low)**: tersine, düşüş yapısı\n\n"
        "Yükselen trend = HH + HL dizisi. Bu dizi bozulduğunda (örn. fiyat LL yaptığında) "
        "trendin zayıfladığının ilk sinyalidir."
    )
    df = _load_df("NVDA").tail(300).reset_index(drop=True)
    swings = analysis.label_market_structure(analysis.find_swings(df, window=10))

    fig = _layout(go.Figure())
    _candles(fig, df)
    shown = 0
    for s in swings:
        if "label" not in s:
            continue
        color = "#3fb27f" if s["label"] in ("HH", "HL") else "#d9534f"
        ay = -35 if s["kind"] == "high" else 35
        _annotate(fig, s["date"], s["price"], s["label"], color=color, ay=ay)
        shown += 1
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"NVDA — son 300 işlem günü. Grafikte {shown} swing noktası otomatik tespit edilip "
        "etiketlendi. Yeşil etiketler (HH/HL) yükseliş yapısını, kırmızılar (LH/LL) bozulmayı gösterir. "
        "Tarihlerin üzerine gelerek her olayın ne zaman olduğunu görebilirsin."
    )


def _lesson_support_resistance():
    st.subheader("Destek ve Direnç")
    st.markdown(
        "**Destek**: fiyatın düşerken tekrar tekrar durduğu seviye — görünmez zemin. "
        "**Direnç**: yükselirken çarpıp döndüğü seviye — görünmez tavan.\n\n"
        "Neden çalışır? Çünkü o seviyelerde daha önce işlem yapmış binlerce kişinin "
        "hafızası vardır: 'oradan almıştım', 'oradan kaçırmıştım'. Seviye ne kadar çok "
        "test edilirse o kadar önemlidir. **Kırılan direnç desteğe dönüşür** — bu, teknik "
        "analizin en klasik kurallarından biridir."
    )
    df = _load_df("AAPL").tail(350).reset_index(drop=True)
    levels = analysis.find_support_resistance(df, window=10, tolerance=0.02, min_touches=3)

    fig = _layout(go.Figure())
    _candles(fig, df)
    for lv in levels:
        fig.add_hline(y=lv["price"], line_dash="dot", line_color="#d9a441", line_width=1.5)
        fig.add_annotation(
            x=df["date"].iloc[-1], y=lv["price"], text=f"{lv['touches']} kez test edildi",
            showarrow=False, font=dict(color="#d9a441", size=11), xanchor="right",
            bgcolor="rgba(11,15,23,0.8)",
        )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("AAPL — son 350 işlem günü. Noktalı çizgiler, fiyatın en az 3 kez döndüğü seviyeler.")
    for lv in levels:
        dates = ", ".join(lv["dates"][:4])
        st.write(f"- **${lv['price']:.2f}** seviyesi {lv['touches']} kez test edildi. Dönüş tarihlerinden bazıları: {dates}")
    term_expander("destek-direnc")


def _lesson_candles():
    st.subheader("Mum Formasyonları")
    st.markdown(
        "Tek bir mum bile bir savaşın özetidir: kim kazandı — alıcılar mı satıcılar mı?\n\n"
        "- **Doji**: açılış ≈ kapanış. Kararsızlık; trend sonlarında görülürse dönüş uyarısı.\n"
        "- **Çekiç (Hammer)**: uzun alt fitil, küçük gövde. Düşüşte görülürse 'satıcılar bastırdı "
        "ama alıcılar günü kurtardı' demektir — potansiyel dip sinyali.\n"
        "- **Kayan Yıldız (Shooting Star)**: uzun üst fitil. Yükselişte görülürse tepe uyarısı.\n"
        "- **Yutan (Engulfing)**: bir mumun gövdesi önceki mumu tamamen yutar. Yutan boğa "
        "yukarı, yutan ayı aşağı dönüş sinyalidir.\n\n"
        "**Önemli:** Tek mum tek başına yetmez — bulunduğu yere (destekte mi, dirençte mi, "
        "trendin neresinde) ve hacme birlikte bakılır."
    )
    df = _load_df("TSLA").tail(150).reset_index(drop=True)
    patterns = analysis.find_candle_patterns(df)

    # Her türden en güncel örneği işaretle
    latest_by_type: dict[str, dict] = {}
    for p in patterns:
        latest_by_type[p["pattern"]] = p

    fig = _layout(go.Figure())
    _candles(fig, df)
    for p in latest_by_type.values():
        ay = 40 if p["pattern"] in ("hammer", "bullish_engulfing") else -40
        _annotate(fig, p["date"], p["price"], PATTERN_TR[p["pattern"]], ay=ay)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("TSLA — son 150 işlem günü. Her formasyon türünün en güncel örneği işaretlendi.")
    for p in sorted(latest_by_type.values(), key=lambda x: x["date"]):
        st.write(f"- **{PATTERN_TR[p['pattern']]}** — {p['date']} tarihinde oluştu.")
    term_expander("mum-grafigi")


def _lesson_ma():
    st.subheader("Hareketli Ortalamalar ve Altın Kesişim")
    st.markdown(
        "**SMA** son X günün basit ortalamasıdır; **EMA** yakın günlere daha çok ağırlık verir, "
        "bu yüzden fiyata daha hızlı tepki verir.\n\n"
        "En ünlü sinyal: **Altın Kesişim (Golden Cross)** — 50 günlük ortalama, 200 günlüğü "
        "yukarı keser → uzun vadeli yükseliş başlangıcı olarak yorumlanır. Tersi **Ölüm "
        "Kesişimi (Death Cross)** — 50, 200'ün altına iner.\n\n"
        "Ortalamalar **gecikmeli** göstergelerdir: trendi başlatmaz, teyit eder. Yatay "
        "piyasada sık sık yanlış sinyal üretirler — bu yüzden tek başına değil, piyasa "
        "yapısı ve hacimle birlikte kullanılır."
    )
    df = _load_df("MU").reset_index(drop=True)
    crosses = analysis.find_ma_crosses(df, 50, 200)
    f50, s200 = analysis.sma(df["close"], 50), analysis.sma(df["close"], 200)

    fig = _layout(go.Figure())
    _candles(fig, df)
    fig.add_trace(go.Scatter(x=df["date"], y=f50, line=dict(color="#58a6ff", width=1.5), name="SMA 50"))
    fig.add_trace(go.Scatter(x=df["date"], y=s200, line=dict(color="orange", width=2), name="SMA 200"))
    for c in crosses:
        if c["type"] == "golden":
            _annotate(fig, c["date"], c["price"], f"Altın Kesişim<br>{c['date']}", color="#3fb27f", ay=45)
        else:
            _annotate(fig, c["date"], c["price"], f"Ölüm Kesişimi<br>{c['date']}", color="#d9534f", ay=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("MU — son 5 yıl. Mavi: SMA 50, turuncu: SMA 200. Tüm kesişimler gerçek tarihleriyle işaretli.")
    for c in crosses:
        adlandirma = "Altın Kesişim (50 > 200)" if c["type"] == "golden" else "Ölüm Kesişimi (50 < 200)"
        st.write(f"- **{c['date']}** — {adlandirma}, fiyat o gün ${c['price']:.2f} idi.")
    term_expander("hareketli-ortalama")


def _lesson_rsi():
    st.subheader("RSI ile Momentum")
    st.markdown(
        "**RSI** fiyatın son 14 gündeki kazanç/kayıp dengesini 0-100 arası puanlar.\n\n"
        "- **70 üzeri = aşırı alım**: yükseliş çok hızlandı, soluklanma gelebilir\n"
        "- **30 altı = aşırı satım**: düşüş aşırılaştı, tepki yükselişi gelebilir\n\n"
        "**Kritik incelik:** Güçlü trendlerde RSI uzun süre aşırı bölgede kalabilir. "
        "'RSI 70 oldu, hemen sat' yaklaşımı güçlü boğa piyasasında sürekli erken sattırır. "
        "Osilatörler en iyi **yatay piyasada** çalışır; trendli piyasada trend yönündeki "
        "sinyalleri tercih et."
    )
    df = _load_df("TSLA").tail(300).reset_index(drop=True)
    r = analysis.rsi(df["close"])
    extremes = analysis.find_rsi_extremes(df)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                        subplot_titles=("Fiyat", "RSI (14)"))
    _candles(fig, df, row=1)
    fig.add_trace(go.Scatter(x=df["date"], y=r, line=dict(color="#d9a441", width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#d9534f", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#3fb27f", row=2, col=1)
    shown = [e for e in extremes if e["date"] >= df["date"].iloc[0]][-6:]
    for e in shown:
        if e["type"] == "oversold":
            _annotate(fig, e["date"], e["price"], f"RSI {e['rsi']}<br>aşırı satım", color="#3fb27f", ay=40)
        else:
            _annotate(fig, e["date"], e["price"], f"RSI {e['rsi']}<br>aşırı alım", color="#d9534f", ay=-40)
    _layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("TSLA — son 300 işlem günü. RSI'ın 30 altına indiği / 70 üstüne çıktığı son 6 giriş işaretli.")
    for e in shown:
        durum = "aşırı satım bölgesine girdi (RSI < 30)" if e["type"] == "oversold" else "aşırı alım bölgesine girdi (RSI > 70)"
        st.write(f"- **{e['date']}** — RSI {e['rsi']} ile {durum}. Sonrasında ne olduğuna grafikten bak!")
    term_expander("rsi")


def _lesson_bollinger():
    st.subheader("Bollinger Bantları ve Volatilite")
    st.markdown(
        "Bollinger Bantları = 20 günlük ortalama ± 2 standart sapma. Bantlar volatiliteyle "
        "nefes alır: sakin dönemde daralır, hareketli dönemde genişler.\n\n"
        "- **Daralma (squeeze)**: sıkışma → genelde büyük bir hareketin habercisi (yönü söylemez!)\n"
        "- Fiyatın bant dışına taşması nadirdir; taşınca genelde ya güçlü trend başlıyordur "
        "ya da hızlı bir geri dönüş gelir.\n\n"
        "**ATR (Average True Range)** ise günlük ortalama hareket genişliğidir — 'bu hisse "
        "günde ortalama kaç dolar oynuyor?' sorusunun cevabı. Stop-loss mesafesini sabit "
        "yüzdeyle değil ATR ile belirlemek, hissenin karakterine uyum sağlar."
    )
    df = _load_df("MSFT").tail(250).reset_index(drop=True)
    mid, up, lo = analysis.bollinger(df["close"])
    width = (up - lo) / mid
    squeeze_idx = width.idxmin() if width.notna().any() else None
    a = analysis.atr(df)

    fig = _layout(go.Figure())
    _candles(fig, df)
    fig.add_trace(go.Scatter(x=df["date"], y=up, line=dict(color="#58a6ff", width=1), name="Üst Bant"))
    fig.add_trace(go.Scatter(x=df["date"], y=mid, line=dict(color="#d9a441", width=1), name="Orta (SMA20)"))
    fig.add_trace(go.Scatter(x=df["date"], y=lo, line=dict(color="#58a6ff", width=1), name="Alt Bant",
                             fill="tonexty", fillcolor="rgba(88,166,255,0.06)"))
    if squeeze_idx is not None and pd.notna(width.loc[squeeze_idx]):
        _annotate(fig, df.loc[squeeze_idx, "date"], mid.loc[squeeze_idx],
                  f"En dar sıkışma<br>{df.loc[squeeze_idx, 'date']}", ay=-50)
    st.plotly_chart(fig, use_container_width=True)
    last_atr = a.iloc[-1]
    st.caption(
        f"MSFT — son 250 işlem günü. Bantların en dar olduğu gün (sıkışma) işaretli — "
        f"sonrasında ne olduğuna dikkat et. Güncel ATR(14): ${last_atr:.2f} "
        f"(hisse şu sıralar günde ortalama bu kadar hareket ediyor)."
    )
    term_expander("volatilite")


def _lesson_volume():
    st.subheader("Hacim Analizi: Teyit ve Kuruma")
    st.markdown(
        "Fiyat 'ne' olduğunu, hacim 'kaç kişinin katıldığını' söyler.\n\n"
        "- **Kırılımda hacim teyidi**: direnç kırılırken hacim ortalamanın belirgin üstünde "
        "olmalı. Düşük hacimli kırılımların çoğu **fakeout** (yanlış kırılım) çıkar.\n"
        "- **Hacim kuruması (VDU)**: konsolidasyonda hacmin ortalamanın yarısına inmesi — "
        "satıcıların bittiğinin işareti, patlama öncesi sessizlik olabilir.\n"
        "- **Toplama/dağıtım**: yükseliş günleri yüksek, düşüş günleri düşük hacimliyse "
        "büyük oyuncu topluyor demektir; tersi dağıtım işaretidir."
    )
    df = _load_df("NVDA").tail(250).reset_index(drop=True)
    vol_ma = df["volume"].rolling(50).mean()
    vdu = [e for e in analysis.find_volume_dry_up(df) if e["date"] >= df["date"].iloc[0]]
    spike_idx = df["volume"].idxmax()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                        subplot_titles=("Fiyat", "Hacim + 50 günlük ortalama"))
    _candles(fig, df, row=1)
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color="rgba(31,119,180,0.5)", name="Hacim"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=vol_ma, line=dict(color="orange", width=2), name="Hacim MA50"), row=2, col=1)
    _annotate(fig, df.loc[spike_idx, "date"], df.loc[spike_idx, "high"],
              f"En yüksek hacim<br>{df.loc[spike_idx, 'date']}", ay=-45)
    for e in vdu[-3:]:
        _annotate(fig, e["date"], e["price"], "VDU (hacim kurudu)", color="#58a6ff", ay=40)
    _layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"NVDA — son 250 işlem günü. En yüksek hacimli gün ({df.loc[spike_idx, 'date']}) ve "
        "hacmin kuruduğu son günler işaretli. Hacim patlamasının olduğu gün fiyatta ne "
        "olduğuna bak — genelde önemli bir haber/kazanç açıklaması vardır."
    )
    term_expander("hacim")


def _lesson_gaps():
    st.subheader("Gap (Boşluk) Türleri")
    st.markdown(
        "**Gap**, bugünün açılışının dünkü kapanıştan kopuk olmasıdır — genelde seans "
        "dışında gelen haberle (kazanç açıklaması, ürün duyurusu) oluşur.\n\n"
        "- **Breakaway gap**: konsolidasyondan kopuş — yeni trendin başlangıcı, en değerlisi\n"
        "- **Runaway gap**: trend ortasında ivmelenme — trend güçlü devam ediyor\n"
        "- **Exhaustion gap**: trendin sonunda son bir coşku — sonrasında dönüş gelir\n\n"
        "Ayrım geriye dönük netleşir; gerçek zamanda kesin bilemezsin. Pratik kural: "
        "gap sonrası hacim ve fiyatın gap'i 'doldurup doldurmadığı' izlenir."
    )
    df = _load_df("NVDA").reset_index(drop=True)
    gaps = sorted(analysis.find_gaps(df, min_gap_pct=5.0), key=lambda g: -abs(g["gap_pct"]))[:6]

    fig = _layout(go.Figure())
    _candles(fig, df)
    for g in gaps:
        color = "#3fb27f" if g["direction"] == "up" else "#d9534f"
        ay = -45 if g["direction"] == "up" else 45
        _annotate(fig, g["date"], g["price"], f"Gap {g['gap_pct']:+}%<br>{g['date']}", color=color, ay=ay)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("NVDA — son 5 yıl. En büyük 6 gap gerçek tarihleriyle işaretli.")
    for g in sorted(gaps, key=lambda x: x["date"]):
        yon = "yukarı" if g["direction"] == "up" else "aşağı"
        st.write(
            f"- **{g['date']}** — fiyat bir önceki kapanışa göre **%{abs(g['gap_pct'])} {yon}** "
            f"boşlukla açıldı. O tarihte hangi haberin çıktığını araştır — gap'lerin arkasında "
            "neredeyse her zaman bir katalizör vardır (çoğunlukla kazanç açıklaması)."
        )


def _lesson_fibonacci():
    st.subheader("Fibonacci Düzeltmeleri")
    st.markdown(
        "Güçlü bir hareketten sonra fiyat genelde tamamını geri vermez — bir kısmını "
        "'düzeltir' ve trend yönüne devam eder. Fibonacci seviyeleri (%23.6, %38.2, %50, "
        "%61.8) bu düzeltmenin nerede durabileceğine dair klasik referanslardır.\n\n"
        "- Sığ düzeltme (%23.6-38.2) = güçlü trend\n"
        "- %61.8'in kaybı = hareketin sorgulanması\n\n"
        "Neden çalışır? Kısmen kendini gerçekleştiren kehanet: milyonlarca trader aynı "
        "seviyelere bakıyor. Tek başına sinyal değil, **diğer araçlarla kesişince** "
        "(destek + fib + yatay seviye = confluence) güçlenir."
    )
    df = _load_df("NVDA").reset_index(drop=True)
    swing = analysis.biggest_swing(df)
    levels = analysis.fibonacci_levels(swing["low"], swing["high"])

    fig = _layout(go.Figure())
    _candles(fig, df)
    for name, price in levels.items():
        fig.add_hline(y=price, line_dash="dot", line_color="#d9a441", line_width=1)
        fig.add_annotation(x=df["date"].iloc[-1], y=price, text=f"{name}: ${price:.2f}",
                           showarrow=False, xanchor="right", font=dict(color="#d9a441", size=10),
                           bgcolor="rgba(11,15,23,0.8)")
    _annotate(fig, swing["low_date"], swing["low"], f"Dip<br>{swing['low_date']}", color="#3fb27f", ay=45)
    _annotate(fig, swing["high_date"], swing["high"], f"Tepe<br>{swing['high_date']}", color="#d9534f", ay=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"NVDA — verideki en büyük dip→tepe hareketi: {swing['low_date']} (${swing['low']:.2f}) → "
        f"{swing['high_date']} (${swing['high']:.2f}). Fibonacci seviyeleri bu harekete göre çizildi. "
        "Fiyatın düzeltmelerde hangi seviyelerde durduğuna dikkat et."
    )


def _lesson_risk():
    st.subheader("Risk Yönetimi: Stop, Hedef, R:R")
    st.markdown(
        "Teknik bilgi işlemin %30'u, risk yönetimi %70'idir. Üç kural:\n\n"
        "1. **Stop-loss her işlemde önceden belli olmalı.** ATR bazlı stop, sabit yüzdeden "
        "iyidir: volatil hissede geniş, sakin hissede dar durur.\n"
        "2. **Risk/Ödül (R:R) en az 1:2 olmalı.** 1 birim riske karşı 2 birim hedef — böylece "
        "%40 isabetle bile kârda kalırsın.\n"
        "3. **Pozisyon büyüklüğü**: tek işlemde sermayenin en fazla %1-2'si riske edilir. "
        "Formül: risk edilecek tutar ÷ (giriş − stop) = alınacak adet.\n\n"
        "**Beklenti (expectancy)** = (kazanma oranı × ort. kazanç) − (kaybetme oranı × ort. kayıp). "
        "Pozitifse sistem uzun vadede kazandırır — tek işlemin sonucu önemli değildir."
    )
    df = _load_df("AAPL").tail(120).reset_index(drop=True)
    a = analysis.atr(df)
    entry = float(df["close"].iloc[-1])
    last_atr = float(a.iloc[-1])
    stop = entry - 2 * last_atr
    target = entry + 4 * last_atr

    fig = _layout(go.Figure())
    _candles(fig, df)
    for price, name, color in [
        (entry, f"Giriş ${entry:.2f}", "#d9a441"),
        (stop, f"Stop ${stop:.2f} (giriş − 2×ATR)", "#d9534f"),
        (target, f"Hedef ${target:.2f} (giriş + 4×ATR) → R:R = 1:2", "#3fb27f"),
    ]:
        fig.add_hline(y=price, line_dash="dash", line_color=color, line_width=1.5)
        fig.add_annotation(x=df["date"].iloc[0], y=price, text=name, showarrow=False,
                           xanchor="left", font=dict(color=color, size=11), bgcolor="rgba(11,15,23,0.8)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"AAPL — son 120 işlem günü üzerinde örnek işlem planı. Güncel ATR(14) = ${last_atr:.2f}. "
        f"Bu plana göre 10.000$ sermayede %1 risk = 100$; (giriş − stop) = ${entry - stop:.2f} "
        f"olduğundan alınabilecek adet = {int(100 / (entry - stop))} hisse. "
        "Stop'suz işlem, plansız uçuş gibidir."
    )
    term_expander("stop-loss")


def _lesson_qullamaggie():
    st.subheader("Qullamaggie Swing Stratejisi — 3 Zamansız Setup")
    st.markdown(
        "**Kristjan Kullamägi (Qullamaggie)**, birkaç bin dolardan yüzlerce milyon dolara "
        "swing trade ile ulaşmış İsveçli bir trader. Sistemi üç basit ama acımasızca "
        "disiplinli setup'a dayanır. Felsefesinin özü:\n\n"
        "> *Tahmin etme, tepki ver. Setup yoksa işlem de yok.*\n\n"
        "**Sistemin ortak omurgası:**\n"
        "- Sadece **en güçlü hisselerde** işlem: son 1/3/6 ayda en çok yükselen %1-2'lik dilim "
        "(göreceli güç filtresi)\n"
        "- İşlem başına risk: hesabın **%0.25-1'i** — asla daha fazlası\n"
        "- Giriş: **opening range high** (ilk 1/5/60 dakikalık mumun tepesinin kırılması)\n"
        "- Stop: **günün en düşüğü** — ve asla ADR'den (günlük ortalama hareket) geniş değil\n"
        "- Kâr alma: 3-5 gün içinde pozisyonun 1/3-1/2'si satılır, kalan **10/20 günlük "
        "ortalama kırılana kadar** taşınır. Boğa piyasasında 10-20R'lik hareketler yakalanır."
    )

    tab1, tab2, tab3 = st.tabs(["Setup 1: Breakout", "Setup 2: Episodic Pivot", "Setup 3: Parabolic"])

    with tab1:
        _qulla_breakout()
    with tab2:
        _qulla_ep()
    with tab3:
        _qulla_parabolic()

    st.divider()
    st.markdown(
        "**Bu stratejiden alınacak asıl dersler** (setup'lardan bile önemli):\n\n"
        "1. **Uzmanlaşma**: Qullamaggie yıllarca sadece bu 3 setup'ı işledi. Her şeyi "
        "yapmaya çalışan hiçbir şeyde iyi olamaz.\n"
        "2. **İşlem günlüğü**: 7-8 yıl boyunca binlerce setup'ın ekran görüntüsünü arşivledi. "
        "Desen tanıma yeteneği bu arşivden geldi — yetenek değil, tekrar.\n"
        "3. **Asimetri**: Küçük ve sabit risk (%0.25-1), açık uçlu kazanç (10-20R). "
        "İsabet oranı %30-40 bile olsa sistem kazandırır.\n"
        "4. **Piyasa filtresi**: Ayı piyasasında bu setup'ların çoğu çalışmaz — o dönemde "
        "az işlem, küçük boyut ya da hiç işlem yapılmaz.\n"
        "5. **Sabır iki yerde gerekir**: setup beklerken ve kazananı taşırken. "
        "Kaybeden işlemde sabır ise en pahalı hatadır."
    )


def _qulla_breakout():
    st.markdown(
        "**Mantık:** Güçlü yükselen hisse (%30-100+ hareket) soluklanır, 10/20 günlük "
        "ortalamaların üzerinde 2 hafta - 2 ay **dar bir bayrak/taban** kurar (bu sırada "
        "hacim kurur — VDU), sonra tabanın tepesini **yüksek hacimle** kırar. Giriş kırılım "
        "anında, stop günün dibinde.\n\n"
        "**Kontrol listesi:**\n"
        "1. Öncesinde güçlü hareket var mı (1-3 ayda %30+)?\n"
        "2. Konsolidasyon dar mı ve 10/20 MA üzerinde mi tutunuyor?\n"
        "3. Hacim konsolidasyonda kurudu mu, kırılımda patladı mı?\n"
        "4. Genel piyasa (QQQ/SPY) yükseliş trendinde mi?"
    )
    # Tüm sembollerde gerçek breakout örnekleri ara
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_breakout_setups(df):
            found.append((sym, e, df))
    if not found:
        st.info("Mevcut verilerde kriterlere tam uyan breakout örneği bulunamadı.")
        return

    sym, e, df = found[-1]  # en güncel örnek
    win = df.iloc[max(0, e["index"] - 90): min(len(df), e["index"] + 40)].reset_index(drop=True)
    ma10 = analysis.sma(win["close"], 10)
    ma20 = analysis.sma(win["close"], 20)

    fig = _layout(go.Figure())
    _candles(fig, win)
    fig.add_trace(go.Scatter(x=win["date"], y=ma10, line=dict(color="#58a6ff", width=1), name="SMA 10"))
    fig.add_trace(go.Scatter(x=win["date"], y=ma20, line=dict(color="orange", width=1.5), name="SMA 20"))
    fig.add_vrect(x0=e["cons_start"], x1=e["date"], fillcolor="rgba(217,164,65,0.12)", line_width=0)
    fig.add_hline(y=e["cons_high"], line_dash="dot", line_color="#d9a441", line_width=1)
    _annotate(fig, e["date"], e["price"], f"KIRILIM<br>{e['date']}", color="#3fb27f", ay=-50)
    _annotate(fig, e["date"], e["stop"], f"Stop: günün dibi<br>${e['stop']:.2f}", color="#d9534f", ay=45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"{sym} — {e['date']} tarihli GERÇEK breakout: öncesinde %{e['run_pct']} yükseliş, "
        f"sarı bölge = konsolidasyon (taban), noktalı çizgi = kırılan tepe (${e['cons_high']:.2f}). "
        "Kırılım günü hacim 50 günlük ortalamanın 1.5 katından fazlaydı."
    )
    if len(found) > 1:
        st.markdown("**Veride bulunan diğer gerçek breakout örnekleri:**")
        for s, ev, _ in found[:-1][-4:]:
            st.write(f"- **{s}** — {ev['date']}: öncesinde %{ev['run_pct']} hareket, taban tepesi ${ev['cons_high']:.2f}")


def _qulla_ep():
    st.markdown(
        "**Mantık:** Beklenmedik büyük haber (kazanç sürprizi, FDA onayı, rehberlik artışı) "
        "hissenin kaderini bir gecede değiştirir. Kriterler:\n\n"
        "1. **%10+ gap-up** (bizim taramada %8+ kullanıldı)\n"
        "2. **Dev hacim** — açılıştan itibaren 2 kat üstü\n"
        "3. **Taze hareket** — hisse son 3-6 ayda zaten koşmuş OLMAMALI "
        "(herkesin bildiği hikâyede sürpriz kalmaz)\n"
        "4. Tercihen güçlü büyüme rakamları (EPS ve ciro)\n\n"
        "Giriş yine opening range high, stop günün dibi. EP'nin gücü: bu hareketler "
        "**aylarca sürebilir** — tek kazanç raporu 6 aylık trend başlatabilir. "
        "Qullamaggie'ye göre bu setup'ta ustalaşmak 4-8 kazanç sezonu (1-2 yıl) alır."
    )
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_episodic_pivots(df):
            found.append((sym, e, df))
    if not found:
        st.info("Mevcut verilerde kriterlere uyan Episodic Pivot bulunamadı.")
        return

    found.sort(key=lambda t: t[1]["gap_pct"])
    sym, e, df = found[-1]  # en büyük gap'li örnek
    win = df.iloc[max(0, e["index"] - 60): min(len(df), e["index"] + 90)].reset_index(drop=True)
    ma10 = analysis.sma(win["close"], 10)
    ma20 = analysis.sma(win["close"], 20)

    fig = _layout(go.Figure())
    _candles(fig, win)
    fig.add_trace(go.Scatter(x=win["date"], y=ma10, line=dict(color="#58a6ff", width=1), name="SMA 10"))
    fig.add_trace(go.Scatter(x=win["date"], y=ma20, line=dict(color="orange", width=1.5), name="SMA 20"))
    _annotate(fig, e["date"], e["price"],
              f"EPISODIC PIVOT<br>{e['date']}<br>Gap %{e['gap_pct']}, hacim {e['volume_x']}x", color="#3fb27f", ay=-55)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"{sym} — {e['date']}: fiyat %{e['gap_pct']} gap ile açıldı, hacim ortalamanın "
        f"{e['volume_x']} katıydı. Grafikte gap sonrası aylarca ne olduğuna bak — EP'nin "
        "asıl kazandıranı gap günü değil, sonrasındaki trenddir. O tarihte hangi haberin "
        "çıktığını araştır (büyük ihtimalle kazanç açıklaması)."
    )
    st.markdown("**Veride bulunan diğer gerçek EP örnekleri:**")
    for s, ev, _ in found[:-1][-4:]:
        st.write(f"- **{s}** — {ev['date']}: gap %{ev['gap_pct']}, hacim {ev['volume_x']}x")


def _qulla_parabolic():
    st.markdown(
        "**Mantık:** Bir hisse birkaç günde dikleşerek %50-100+ (küçük hisselerde %300-1000) "
        "yükselirse, art arda 3-5+ yeşil gün geldiyse — bu **parabolik aşırılık** "
        "sürdürülemez. Qullamaggie bu noktada dönüşü SHORT'lar:\n\n"
        "- Giriş: ilk kırmızı 5 dakikalık mum / opening range low\n"
        "- Stop: günün tepesi\n"
        "- Hedef: **10/20 günlük ortalamaya dönüş** (lastik bandın gevşemesi)\n"
        "- Tek intraday göstergesi: **VWAP**\n\n"
        "R:R bu setup'ta 5-10x'tir ama isabet oranı yüksektir. **Uyarı:** açığa satış "
        "sınırsız zarar riski taşır — bu setup en tecrübe isteyenidir. Bizim gibi "
        "öğrenenler için asıl değeri şudur: parabolik yükselişte ASLA alım kovalama."
    )
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_parabolic_moves(df):
            found.append((sym, e, df))
    if not found:
        st.info(
            "Mevcut 5 büyük hissede son 5 yılda bu kriterlere (%30+/7 gün) uyan parabolik "
            "hareket bulunamadı — bu setup daha çok küçük, spekülatif hisselerde görülür. "
            "Bu da başlı başına bir ders: büyük şirketler nadiren parabolik olur."
        )
        return

    found.sort(key=lambda t: t[1]["gain_pct"])
    sym, e, df = found[-1]
    win = df.iloc[max(0, e["index"] - 40): min(len(df), e["index"] + 40)].reset_index(drop=True)
    ma10 = analysis.sma(win["close"], 10)
    ma20 = analysis.sma(win["close"], 20)

    fig = _layout(go.Figure())
    _candles(fig, win)
    fig.add_trace(go.Scatter(x=win["date"], y=ma10, line=dict(color="#58a6ff", width=1), name="SMA 10"))
    fig.add_trace(go.Scatter(x=win["date"], y=ma20, line=dict(color="orange", width=1.5), name="SMA 20"))
    _annotate(fig, e["date"], e["price"],
              f"PARABOLİK<br>{e['date']}<br>7 günde +%{e['gain_pct']}", color="#d9534f", ay=-55)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"{sym} — {e['date']}: 7 işlem gününde %{e['gain_pct']} yükseliş. Sonrasında "
        "fiyatın 10/20 günlük ortalamalara (mavi/turuncu) nasıl geri çekildiğine bak — "
        "parabolik hareketlerin 'yerçekimi' budur."
    )
    if len(found) > 1:
        st.markdown("**Veride bulunan diğer parabolik hareketler:**")
        for s, ev, _ in found[:-1][-4:]:
            st.write(f"- **{s}** — {ev['date']}: 7 günde +%{ev['gain_pct']}")
