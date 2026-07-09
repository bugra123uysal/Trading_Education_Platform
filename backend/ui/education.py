"""
Teknik Analiz Eğitimi sayfası.

Her ders: kavramın sade anlatımı + GERÇEK hisse grafiği üzerinde,
gerçek tarihlerle işaretlenmiş örnekler. İşaretlerin hepsi
app/analysis.py'deki tespit fonksiyonlarıyla veriden bulunur —
"bu olay bu tarihte gerçekten oldu" garantisi budur.

Metinler iki dillidir: _L(tr, en) seçili dile göre uygun metni döndürür.
Yoğun anlatım prose'u için bu, ayrı bir sözlük yerine TR/EN metni yan yana
tutmanın en okunur yoludur.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app import analysis
from app.data.fetcher import get_candles
from app.database import session_scope
from app.i18n import get_lang, t
from ui.common import term_expander


def _L(tr: str, en: str) -> str:
    """Seçili dile göre metni döndürür."""
    return en if get_lang() == "en" else tr


def _pattern_label(pattern: str) -> str:
    return {
        "doji": _L("Doji", "Doji"),
        "hammer": _L("Çekiç (Hammer)", "Hammer"),
        "shooting_star": _L("Kayan Yıldız (Shooting Star)", "Shooting Star"),
        "bullish_engulfing": _L("Yutan Boğa (Bullish Engulfing)", "Bullish Engulfing"),
        "bearish_engulfing": _L("Yutan Ayı (Bearish Engulfing)", "Bearish Engulfing"),
    }[pattern]


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
        increasing_fillcolor="#3fb27f", decreasing_fillcolor="#d9534f", name=_L("Fiyat", "Price"),
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
    st.title(t("edu_title"))
    st.write(t("edu_intro"))

    # (tr_ad, en_ad, fonksiyon)
    lessons = [
        ("1. Trend ve Piyasa Yapısı (HH/HL)", "1. Trend & Market Structure (HH/HL)", _lesson_trend),
        ("2. Destek ve Direnç", "2. Support & Resistance", _lesson_support_resistance),
        ("3. Mum Formasyonları", "3. Candlestick Patterns", _lesson_candles),
        ("4. Hareketli Ortalamalar ve Altın Kesişim", "4. Moving Averages & Golden Cross", _lesson_ma),
        ("5. RSI ile Momentum", "5. Momentum with RSI", _lesson_rsi),
        ("6. Bollinger Bantları ve Volatilite", "6. Bollinger Bands & Volatility", _lesson_bollinger),
        ("7. Hacim Analizi: Teyit ve Kuruma", "7. Volume Analysis: Confirmation & Dry-Up", _lesson_volume),
        ("8. Gap (Boşluk) Türleri", "8. Gap Types", _lesson_gaps),
        ("9. Fibonacci Düzeltmeleri", "9. Fibonacci Retracements", _lesson_fibonacci),
        ("10. Risk Yönetimi: Stop, Hedef, R:R", "10. Risk Management: Stop, Target, R:R", _lesson_risk),
        ("11. Qullamaggie Swing Stratejisi (3 Setup)", "11. Qullamaggie Swing Strategy (3 Setups)", _lesson_qullamaggie),
    ]
    labels = [_L(tr, en) for tr, en, _ in lessons]
    choice = st.selectbox(t("edu_select_lesson"), options=labels)
    st.divider()
    lessons[labels.index(choice)][2]()


# ---------- Dersler ----------

def _lesson_trend():
    st.subheader(_L("Trend ve Piyasa Yapısı", "Trend & Market Structure"))
    st.markdown(_L(
        "Fiyat üç yönde hareket eder: **yükselen trend**, **düşen trend**, **yatay**. "
        "Trendi tanımanın en sağlam yolu tepe ve dipleri izlemektir:\n\n"
        "- **HH (Higher High)**: bir önceki tepeden daha yüksek tepe → yükseliş sürüyor\n"
        "- **HL (Higher Low)**: bir önceki dipten daha yüksek dip → alıcılar erken davranıyor\n"
        "- **LH (Lower High)** ve **LL (Lower Low)**: tersine, düşüş yapısı\n\n"
        "Yükselen trend = HH + HL dizisi. Bu dizi bozulduğunda (örn. fiyat LL yaptığında) "
        "trendin zayıfladığının ilk sinyalidir.",
        "Price moves in three directions: **uptrend**, **downtrend**, **sideways**. The most "
        "reliable way to recognize a trend is to track the peaks and troughs:\n\n"
        "- **HH (Higher High)**: a peak higher than the previous one → the rise continues\n"
        "- **HL (Higher Low)**: a trough higher than the previous one → buyers step in early\n"
        "- **LH (Lower High)** and **LL (Lower Low)**: conversely, a downtrend structure\n\n"
        "An uptrend = a sequence of HH + HL. When this sequence breaks (e.g. price makes an LL) "
        "it's the first sign the trend is weakening.",
    ))
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
    st.caption(_L(
        f"NVDA — son 300 işlem günü. Grafikte {shown} swing noktası otomatik tespit edilip "
        "etiketlendi. Yeşil etiketler (HH/HL) yükseliş yapısını, kırmızılar (LH/LL) bozulmayı gösterir. "
        "Tarihlerin üzerine gelerek her olayın ne zaman olduğunu görebilirsin.",
        f"NVDA — last 300 trading days. {shown} swing points were detected and labeled "
        "automatically. Green labels (HH/HL) show the uptrend structure, red ones (LH/LL) show "
        "the breakdown. Hover over the dates to see when each event happened.",
    ))


def _lesson_support_resistance():
    st.subheader(_L("Destek ve Direnç", "Support & Resistance"))
    st.markdown(_L(
        "**Destek**: fiyatın düşerken tekrar tekrar durduğu seviye — görünmez zemin. "
        "**Direnç**: yükselirken çarpıp döndüğü seviye — görünmez tavan.\n\n"
        "Neden çalışır? Çünkü o seviyelerde daha önce işlem yapmış binlerce kişinin "
        "hafızası vardır: 'oradan almıştım', 'oradan kaçırmıştım'. Seviye ne kadar çok "
        "test edilirse o kadar önemlidir. **Kırılan direnç desteğe dönüşür** — bu, teknik "
        "analizin en klasik kurallarından biridir.",
        "**Support**: the level where a falling price repeatedly stops — an invisible floor. "
        "**Resistance**: the level where a rising price bumps and turns back — an invisible ceiling.\n\n"
        "Why does it work? Because thousands of people who traded at those levels remember them: "
        "'I bought there', 'I missed it there'. The more a level is tested, the more important it "
        "is. **Broken resistance turns into support** — one of the most classic rules in "
        "technical analysis.",
    ))
    df = _load_df("AAPL").tail(350).reset_index(drop=True)
    levels = analysis.find_support_resistance(df, window=10, tolerance=0.02, min_touches=3)

    fig = _layout(go.Figure())
    _candles(fig, df)
    for lv in levels:
        fig.add_hline(y=lv["price"], line_dash="dot", line_color="#d9a441", line_width=1.5)
        fig.add_annotation(
            x=df["date"].iloc[-1], y=lv["price"],
            text=_L(f"{lv['touches']} kez test edildi", f"tested {lv['touches']} times"),
            showarrow=False, font=dict(color="#d9a441", size=11), xanchor="right",
            bgcolor="rgba(11,15,23,0.8)",
        )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        "AAPL — son 350 işlem günü. Noktalı çizgiler, fiyatın en az 3 kez döndüğü seviyeler.",
        "AAPL — last 350 trading days. Dotted lines are levels where price turned at least 3 times.",
    ))
    for lv in levels:
        dates = ", ".join(lv["dates"][:4])
        st.write(_L(
            f"- **${lv['price']:.2f}** seviyesi {lv['touches']} kez test edildi. Dönüş tarihlerinden bazıları: {dates}",
            f"- The **${lv['price']:.2f}** level was tested {lv['touches']} times. Some of the turn dates: {dates}",
        ))
    term_expander("destek-direnc")


def _lesson_candles():
    st.subheader(_L("Mum Formasyonları", "Candlestick Patterns"))
    st.markdown(_L(
        "Tek bir mum bile bir savaşın özetidir: kim kazandı — alıcılar mı satıcılar mı?\n\n"
        "- **Doji**: açılış ≈ kapanış. Kararsızlık; trend sonlarında görülürse dönüş uyarısı.\n"
        "- **Çekiç (Hammer)**: uzun alt fitil, küçük gövde. Düşüşte görülürse 'satıcılar bastırdı "
        "ama alıcılar günü kurtardı' demektir — potansiyel dip sinyali.\n"
        "- **Kayan Yıldız (Shooting Star)**: uzun üst fitil. Yükselişte görülürse tepe uyarısı.\n"
        "- **Yutan (Engulfing)**: bir mumun gövdesi önceki mumu tamamen yutar. Yutan boğa "
        "yukarı, yutan ayı aşağı dönüş sinyalidir.\n\n"
        "**Önemli:** Tek mum tek başına yetmez — bulunduğu yere (destekte mi, dirençte mi, "
        "trendin neresinde) ve hacme birlikte bakılır.",
        "Even a single candle summarizes a battle: who won — buyers or sellers?\n\n"
        "- **Doji**: open ≈ close. Indecision; at the end of a trend it warns of a reversal.\n"
        "- **Hammer**: long lower wick, small body. In a decline it means 'sellers pressed but "
        "buyers saved the day' — a potential bottom signal.\n"
        "- **Shooting Star**: long upper wick. In a rise it warns of a top.\n"
        "- **Engulfing**: one candle's body completely engulfs the previous one. A bullish "
        "engulfing signals an up-reversal, a bearish one a down-reversal.\n\n"
        "**Important:** A single candle isn't enough on its own — read it together with its "
        "location (support? resistance? where in the trend?) and with volume.",
    ))
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
        _annotate(fig, p["date"], p["price"], _pattern_label(p["pattern"]), ay=ay)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        "TSLA — son 150 işlem günü. Her formasyon türünün en güncel örneği işaretlendi.",
        "TSLA — last 150 trading days. The most recent example of each pattern type is marked.",
    ))
    for p in sorted(latest_by_type.values(), key=lambda x: x["date"]):
        st.write(_L(
            f"- **{_pattern_label(p['pattern'])}** — {p['date']} tarihinde oluştu.",
            f"- **{_pattern_label(p['pattern'])}** — formed on {p['date']}.",
        ))
    term_expander("mum-grafigi")


def _lesson_ma():
    st.subheader(_L("Hareketli Ortalamalar ve Altın Kesişim", "Moving Averages & Golden Cross"))
    st.markdown(_L(
        "**SMA** son X günün basit ortalamasıdır; **EMA** yakın günlere daha çok ağırlık verir, "
        "bu yüzden fiyata daha hızlı tepki verir.\n\n"
        "En ünlü sinyal: **Altın Kesişim (Golden Cross)** — 50 günlük ortalama, 200 günlüğü "
        "yukarı keser → uzun vadeli yükseliş başlangıcı olarak yorumlanır. Tersi **Ölüm "
        "Kesişimi (Death Cross)** — 50, 200'ün altına iner.\n\n"
        "Ortalamalar **gecikmeli** göstergelerdir: trendi başlatmaz, teyit eder. Yatay "
        "piyasada sık sık yanlış sinyal üretirler — bu yüzden tek başına değil, piyasa "
        "yapısı ve hacimle birlikte kullanılır.",
        "**SMA** is the simple average of the last X days; **EMA** weights recent days more, so "
        "it reacts to price faster.\n\n"
        "The most famous signal: the **Golden Cross** — the 50-day average crossing above the "
        "200-day → read as the start of a long-term uptrend. The opposite is the **Death "
        "Cross** — the 50 dropping below the 200.\n\n"
        "Averages are **lagging** indicators: they don't start the trend, they confirm it. In a "
        "sideways market they produce frequent false signals — so use them together with market "
        "structure and volume, not alone.",
    ))
    df = _load_df("MU").reset_index(drop=True)
    crosses = analysis.find_ma_crosses(df, 50, 200)
    f50, s200 = analysis.sma(df["close"], 50), analysis.sma(df["close"], 200)

    fig = _layout(go.Figure())
    _candles(fig, df)
    fig.add_trace(go.Scatter(x=df["date"], y=f50, line=dict(color="#58a6ff", width=1.5), name="SMA 50"))
    fig.add_trace(go.Scatter(x=df["date"], y=s200, line=dict(color="orange", width=2), name="SMA 200"))
    for c in crosses:
        if c["type"] == "golden":
            _annotate(fig, c["date"], c["price"], _L("Altın Kesişim", "Golden Cross") + f"<br>{c['date']}",
                      color="#3fb27f", ay=45)
        else:
            _annotate(fig, c["date"], c["price"], _L("Ölüm Kesişimi", "Death Cross") + f"<br>{c['date']}",
                      color="#d9534f", ay=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        "MU — son 5 yıl. Mavi: SMA 50, turuncu: SMA 200. Tüm kesişimler gerçek tarihleriyle işaretli.",
        "MU — last 5 years. Blue: SMA 50, orange: SMA 200. All crosses are marked with their real dates.",
    ))
    for c in crosses:
        label = (_L("Altın Kesişim (50 > 200)", "Golden Cross (50 > 200)") if c["type"] == "golden"
                 else _L("Ölüm Kesişimi (50 < 200)", "Death Cross (50 < 200)"))
        st.write(_L(
            f"- **{c['date']}** — {label}, fiyat o gün ${c['price']:.2f} idi.",
            f"- **{c['date']}** — {label}, price was ${c['price']:.2f} that day.",
        ))
    term_expander("hareketli-ortalama")


def _lesson_rsi():
    st.subheader(_L("RSI ile Momentum", "Momentum with RSI"))
    st.markdown(_L(
        "**RSI** fiyatın son 14 gündeki kazanç/kayıp dengesini 0-100 arası puanlar.\n\n"
        "- **70 üzeri = aşırı alım**: yükseliş çok hızlandı, soluklanma gelebilir\n"
        "- **30 altı = aşırı satım**: düşüş aşırılaştı, tepki yükselişi gelebilir\n\n"
        "**Kritik incelik:** Güçlü trendlerde RSI uzun süre aşırı bölgede kalabilir. "
        "'RSI 70 oldu, hemen sat' yaklaşımı güçlü boğa piyasasında sürekli erken sattırır. "
        "Osilatörler en iyi **yatay piyasada** çalışır; trendli piyasada trend yönündeki "
        "sinyalleri tercih et.",
        "**RSI** scores the balance of gains/losses over the last 14 days on a 0–100 scale.\n\n"
        "- **Above 70 = overbought**: the rise sped up a lot, a pause may come\n"
        "- **Below 30 = oversold**: the fall got extreme, a relief bounce may come\n\n"
        "**Critical nuance:** In strong trends RSI can stay in the extreme zone for a long time. "
        "The 'RSI hit 70, sell now' approach keeps making you sell too early in a strong bull "
        "market. Oscillators work best in a **sideways market**; in a trending market, prefer "
        "signals in the trend's direction.",
    ))
    df = _load_df("TSLA").tail(300).reset_index(drop=True)
    r = analysis.rsi(df["close"])
    extremes = analysis.find_rsi_extremes(df)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                        subplot_titles=(_L("Fiyat", "Price"), "RSI (14)"))
    _candles(fig, df, row=1)
    fig.add_trace(go.Scatter(x=df["date"], y=r, line=dict(color="#d9a441", width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#d9534f", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#3fb27f", row=2, col=1)
    shown = [e for e in extremes if e["date"] >= df["date"].iloc[0]][-6:]
    for e in shown:
        if e["type"] == "oversold":
            _annotate(fig, e["date"], e["price"], f"RSI {e['rsi']}<br>" + _L("aşırı satım", "oversold"),
                      color="#3fb27f", ay=40)
        else:
            _annotate(fig, e["date"], e["price"], f"RSI {e['rsi']}<br>" + _L("aşırı alım", "overbought"),
                      color="#d9534f", ay=-40)
    _layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        "TSLA — son 300 işlem günü. RSI'ın 30 altına indiği / 70 üstüne çıktığı son 6 giriş işaretli.",
        "TSLA — last 300 trading days. The last 6 entries where RSI dipped below 30 / rose above 70 are marked.",
    ))
    for e in shown:
        status = (_L("aşırı satım bölgesine girdi (RSI < 30)", "entered the oversold zone (RSI < 30)")
                  if e["type"] == "oversold"
                  else _L("aşırı alım bölgesine girdi (RSI > 70)", "entered the overbought zone (RSI > 70)"))
        st.write(_L(
            f"- **{e['date']}** — RSI {e['rsi']} ile {status}. Sonrasında ne olduğuna grafikten bak!",
            f"- **{e['date']}** — with RSI {e['rsi']} it {status}. See what happened next on the chart!",
        ))
    term_expander("rsi")


def _lesson_bollinger():
    st.subheader(_L("Bollinger Bantları ve Volatilite", "Bollinger Bands & Volatility"))
    st.markdown(_L(
        "Bollinger Bantları = 20 günlük ortalama ± 2 standart sapma. Bantlar volatiliteyle "
        "nefes alır: sakin dönemde daralır, hareketli dönemde genişler.\n\n"
        "- **Daralma (squeeze)**: sıkışma → genelde büyük bir hareketin habercisi (yönü söylemez!)\n"
        "- Fiyatın bant dışına taşması nadirdir; taşınca genelde ya güçlü trend başlıyordur "
        "ya da hızlı bir geri dönüş gelir.\n\n"
        "**ATR (Average True Range)** ise günlük ortalama hareket genişliğidir — 'bu hisse "
        "günde ortalama kaç dolar oynuyor?' sorusunun cevabı. Stop-loss mesafesini sabit "
        "yüzdeyle değil ATR ile belirlemek, hissenin karakterine uyum sağlar.",
        "Bollinger Bands = 20-day average ± 2 standard deviations. The bands breathe with "
        "volatility: they narrow in calm periods and widen in active ones.\n\n"
        "- **Squeeze**: a tightening → usually heralds a big move (it doesn't tell the direction!)\n"
        "- Price closing outside the bands is rare; when it does, usually either a strong trend "
        "is starting or a quick reversal follows.\n\n"
        "**ATR (Average True Range)** is the average daily move — the answer to 'how many dollars "
        "does this stock swing per day on average?' Setting your stop-loss distance with ATR "
        "rather than a fixed percentage adapts it to the stock's character.",
    ))
    df = _load_df("MSFT").tail(250).reset_index(drop=True)
    mid, up, lo = analysis.bollinger(df["close"])
    width = (up - lo) / mid
    squeeze_idx = width.idxmin() if width.notna().any() else None
    a = analysis.atr(df)

    fig = _layout(go.Figure())
    _candles(fig, df)
    fig.add_trace(go.Scatter(x=df["date"], y=up, line=dict(color="#58a6ff", width=1), name=_L("Üst Bant", "Upper Band")))
    fig.add_trace(go.Scatter(x=df["date"], y=mid, line=dict(color="#d9a441", width=1), name=_L("Orta (SMA20)", "Middle (SMA20)")))
    fig.add_trace(go.Scatter(x=df["date"], y=lo, line=dict(color="#58a6ff", width=1), name=_L("Alt Bant", "Lower Band"),
                             fill="tonexty", fillcolor="rgba(88,166,255,0.06)"))
    if squeeze_idx is not None and pd.notna(width.loc[squeeze_idx]):
        _annotate(fig, df.loc[squeeze_idx, "date"], mid.loc[squeeze_idx],
                  _L("En dar sıkışma", "Tightest squeeze") + f"<br>{df.loc[squeeze_idx, 'date']}", ay=-50)
    st.plotly_chart(fig, use_container_width=True)
    last_atr = a.iloc[-1]
    st.caption(_L(
        f"MSFT — son 250 işlem günü. Bantların en dar olduğu gün (sıkışma) işaretli — "
        f"sonrasında ne olduğuna dikkat et. Güncel ATR(14): ${last_atr:.2f} "
        f"(hisse şu sıralar günde ortalama bu kadar hareket ediyor).",
        f"MSFT — last 250 trading days. The day the bands were tightest (the squeeze) is marked — "
        f"watch what happened next. Current ATR(14): ${last_atr:.2f} "
        f"(roughly how much the stock moves per day lately).",
    ))
    term_expander("volatilite")


def _lesson_volume():
    st.subheader(_L("Hacim Analizi: Teyit ve Kuruma", "Volume Analysis: Confirmation & Dry-Up"))
    st.markdown(_L(
        "Fiyat 'ne' olduğunu, hacim 'kaç kişinin katıldığını' söyler.\n\n"
        "- **Kırılımda hacim teyidi**: direnç kırılırken hacim ortalamanın belirgin üstünde "
        "olmalı. Düşük hacimli kırılımların çoğu **fakeout** (yanlış kırılım) çıkar.\n"
        "- **Hacim kuruması (VDU)**: konsolidasyonda hacmin ortalamanın yarısına inmesi — "
        "satıcıların bittiğinin işareti, patlama öncesi sessizlik olabilir.\n"
        "- **Toplama/dağıtım**: yükseliş günleri yüksek, düşüş günleri düşük hacimliyse "
        "büyük oyuncu topluyor demektir; tersi dağıtım işaretidir.",
        "Price tells you 'what' happened, volume tells you 'how many people participated.'\n\n"
        "- **Volume confirmation on breakouts**: when resistance breaks, volume should be clearly "
        "above average. Most low-volume breakouts turn out to be **fakeouts**.\n"
        "- **Volume Dry-Up (VDU)**: volume falling to half its average during consolidation — a "
        "sign sellers are exhausted, possibly the calm before the breakout.\n"
        "- **Accumulation/distribution**: if up days have high volume and down days low volume, a "
        "big player is accumulating; the reverse signals distribution.",
    ))
    df = _load_df("NVDA").tail(250).reset_index(drop=True)
    vol_ma = df["volume"].rolling(50).mean()
    vdu = [e for e in analysis.find_volume_dry_up(df) if e["date"] >= df["date"].iloc[0]]
    spike_idx = df["volume"].idxmax()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05,
                        subplot_titles=(_L("Fiyat", "Price"), _L("Hacim + 50 günlük ortalama", "Volume + 50-day average")))
    _candles(fig, df, row=1)
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color="rgba(31,119,180,0.5)", name=_L("Hacim", "Volume")), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=vol_ma, line=dict(color="orange", width=2), name=_L("Hacim MA50", "Volume MA50")), row=2, col=1)
    _annotate(fig, df.loc[spike_idx, "date"], df.loc[spike_idx, "high"],
              _L("En yüksek hacim", "Highest volume") + f"<br>{df.loc[spike_idx, 'date']}", ay=-45)
    for e in vdu[-3:]:
        _annotate(fig, e["date"], e["price"], _L("VDU (hacim kurudu)", "VDU (volume dried up)"), color="#58a6ff", ay=40)
    _layout(fig, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"NVDA — son 250 işlem günü. En yüksek hacimli gün ({df.loc[spike_idx, 'date']}) ve "
        "hacmin kuruduğu son günler işaretli. Hacim patlamasının olduğu gün fiyatta ne "
        "olduğuna bak — genelde önemli bir haber/kazanç açıklaması vardır.",
        f"NVDA — last 250 trading days. The highest-volume day ({df.loc[spike_idx, 'date']}) and "
        "the recent volume dry-up days are marked. Look at what price did on the volume-spike day "
        "— there's usually important news / an earnings release behind it.",
    ))
    term_expander("hacim")


def _lesson_gaps():
    st.subheader(_L("Gap (Boşluk) Türleri", "Gap Types"))
    st.markdown(_L(
        "**Gap**, bugünün açılışının dünkü kapanıştan kopuk olmasıdır — genelde seans "
        "dışında gelen haberle (kazanç açıklaması, ürün duyurusu) oluşur.\n\n"
        "- **Breakaway gap**: konsolidasyondan kopuş — yeni trendin başlangıcı, en değerlisi\n"
        "- **Runaway gap**: trend ortasında ivmelenme — trend güçlü devam ediyor\n"
        "- **Exhaustion gap**: trendin sonunda son bir coşku — sonrasında dönüş gelir\n\n"
        "Ayrım geriye dönük netleşir; gerçek zamanda kesin bilemezsin. Pratik kural: "
        "gap sonrası hacim ve fiyatın gap'i 'doldurup doldurmadığı' izlenir.",
        "A **gap** is today's open being disconnected from yesterday's close — usually created by "
        "news arriving outside the session (an earnings release, a product announcement).\n\n"
        "- **Breakaway gap**: a break out of consolidation — the start of a new trend, the most valuable\n"
        "- **Runaway gap**: acceleration mid-trend — the trend continues strongly\n"
        "- **Exhaustion gap**: one last burst at the end of a trend — a reversal follows\n\n"
        "The distinction becomes clear in hindsight; you can't be sure in real time. Practical "
        "rule: watch post-gap volume and whether price 'fills' the gap.",
    ))
    df = _load_df("NVDA").reset_index(drop=True)
    gaps = sorted(analysis.find_gaps(df, min_gap_pct=5.0), key=lambda g: -abs(g["gap_pct"]))[:6]

    fig = _layout(go.Figure())
    _candles(fig, df)
    for g in gaps:
        color = "#3fb27f" if g["direction"] == "up" else "#d9534f"
        ay = -45 if g["direction"] == "up" else 45
        _annotate(fig, g["date"], g["price"], f"Gap {g['gap_pct']:+}%<br>{g['date']}", color=color, ay=ay)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        "NVDA — son 5 yıl. En büyük 6 gap gerçek tarihleriyle işaretli.",
        "NVDA — last 5 years. The 6 largest gaps are marked with their real dates.",
    ))
    for g in sorted(gaps, key=lambda x: x["date"]):
        direction = _L("yukarı", "up") if g["direction"] == "up" else _L("aşağı", "down")
        st.write(_L(
            f"- **{g['date']}** — fiyat bir önceki kapanışa göre **%{abs(g['gap_pct'])} {direction}** "
            f"boşlukla açıldı. O tarihte hangi haberin çıktığını araştır — gap'lerin arkasında "
            "neredeyse her zaman bir katalizör vardır (çoğunlukla kazanç açıklaması).",
            f"- **{g['date']}** — price opened with a **{abs(g['gap_pct'])}% {direction}** gap versus "
            "the prior close. Research what news came out that day — there's almost always a "
            "catalyst behind a gap (usually an earnings release).",
        ))


def _lesson_fibonacci():
    st.subheader(_L("Fibonacci Düzeltmeleri", "Fibonacci Retracements"))
    st.markdown(_L(
        "Güçlü bir hareketten sonra fiyat genelde tamamını geri vermez — bir kısmını "
        "'düzeltir' ve trend yönüne devam eder. Fibonacci seviyeleri (%23.6, %38.2, %50, "
        "%61.8) bu düzeltmenin nerede durabileceğine dair klasik referanslardır.\n\n"
        "- Sığ düzeltme (%23.6-38.2) = güçlü trend\n"
        "- %61.8'in kaybı = hareketin sorgulanması\n\n"
        "Neden çalışır? Kısmen kendini gerçekleştiren kehanet: milyonlarca trader aynı "
        "seviyelere bakıyor. Tek başına sinyal değil, **diğer araçlarla kesişince** "
        "(destek + fib + yatay seviye = confluence) güçlenir.",
        "After a strong move, price usually doesn't give it all back — it 'retraces' part of it "
        "and continues in the trend's direction. Fibonacci levels (23.6%, 38.2%, 50%, 61.8%) are "
        "the classic references for where that retracement might stop.\n\n"
        "- Shallow retracement (23.6–38.2%) = strong trend\n"
        "- Losing the 61.8% level = the move is in question\n\n"
        "Why does it work? Partly a self-fulfilling prophecy: millions of traders watch the same "
        "levels. It's not a signal on its own — it gets stronger **when it overlaps with other "
        "tools** (support + fib + a horizontal level = confluence).",
    ))
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
    _annotate(fig, swing["low_date"], swing["low"], _L("Dip", "Low") + f"<br>{swing['low_date']}", color="#3fb27f", ay=45)
    _annotate(fig, swing["high_date"], swing["high"], _L("Tepe", "High") + f"<br>{swing['high_date']}", color="#d9534f", ay=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"NVDA — verideki en büyük dip→tepe hareketi: {swing['low_date']} (${swing['low']:.2f}) → "
        f"{swing['high_date']} (${swing['high']:.2f}). Fibonacci seviyeleri bu harekete göre çizildi. "
        "Fiyatın düzeltmelerde hangi seviyelerde durduğuna dikkat et.",
        f"NVDA — the largest low→high move in the data: {swing['low_date']} (${swing['low']:.2f}) → "
        f"{swing['high_date']} (${swing['high']:.2f}). The Fibonacci levels are drawn from this move. "
        "Notice which levels price stalls at during retracements.",
    ))


def _lesson_risk():
    st.subheader(_L("Risk Yönetimi: Stop, Hedef, R:R", "Risk Management: Stop, Target, R:R"))
    st.markdown(_L(
        "Teknik bilgi işlemin %30'u, risk yönetimi %70'idir. Üç kural:\n\n"
        "1. **Stop-loss her işlemde önceden belli olmalı.** ATR bazlı stop, sabit yüzdeden "
        "iyidir: volatil hissede geniş, sakin hissede dar durur.\n"
        "2. **Risk/Ödül (R:R) en az 1:2 olmalı.** 1 birim riske karşı 2 birim hedef — böylece "
        "%40 isabetle bile kârda kalırsın.\n"
        "3. **Pozisyon büyüklüğü**: tek işlemde sermayenin en fazla %1-2'si riske edilir. "
        "Formül: risk edilecek tutar ÷ (giriş − stop) = alınacak adet.\n\n"
        "**Beklenti (expectancy)** = (kazanma oranı × ort. kazanç) − (kaybetme oranı × ort. kayıp). "
        "Pozitifse sistem uzun vadede kazandırır — tek işlemin sonucu önemli değildir.",
        "Technical knowledge is 30% of trading, risk management is 70%. Three rules:\n\n"
        "1. **A stop-loss must be set in advance on every trade.** An ATR-based stop beats a fixed "
        "percentage: wide on a volatile stock, tight on a calm one.\n"
        "2. **Risk/Reward (R:R) should be at least 1:2.** 2 units of target for 1 unit of risk — so "
        "you stay profitable even at a 40% hit rate.\n"
        "3. **Position size**: risk at most 1–2% of capital on a single trade. Formula: amount to "
        "risk ÷ (entry − stop) = number of shares.\n\n"
        "**Expectancy** = (win rate × avg win) − (loss rate × avg loss). If it's positive the "
        "system profits long-term — the result of any single trade doesn't matter.",
    ))
    df = _load_df("AAPL").tail(120).reset_index(drop=True)
    a = analysis.atr(df)
    entry = float(df["close"].iloc[-1])
    last_atr = float(a.iloc[-1])
    stop = entry - 2 * last_atr
    target = entry + 4 * last_atr

    fig = _layout(go.Figure())
    _candles(fig, df)
    rows = [
        (entry, _L(f"Giriş ${entry:.2f}", f"Entry ${entry:.2f}"), "#d9a441"),
        (stop, _L(f"Stop ${stop:.2f} (giriş − 2×ATR)", f"Stop ${stop:.2f} (entry − 2×ATR)"), "#d9534f"),
        (target, _L(f"Hedef ${target:.2f} (giriş + 4×ATR) → R:R = 1:2",
                    f"Target ${target:.2f} (entry + 4×ATR) → R:R = 1:2"), "#3fb27f"),
    ]
    for price, name, color in rows:
        fig.add_hline(y=price, line_dash="dash", line_color=color, line_width=1.5)
        fig.add_annotation(x=df["date"].iloc[0], y=price, text=name, showarrow=False,
                           xanchor="left", font=dict(color=color, size=11), bgcolor="rgba(11,15,23,0.8)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"AAPL — son 120 işlem günü üzerinde örnek işlem planı. Güncel ATR(14) = ${last_atr:.2f}. "
        f"Bu plana göre 10.000$ sermayede %1 risk = 100$; (giriş − stop) = ${entry - stop:.2f} "
        f"olduğundan alınabilecek adet = {int(100 / (entry - stop))} hisse. "
        "Stop'suz işlem, plansız uçuş gibidir.",
        f"AAPL — an example trade plan over the last 120 trading days. Current ATR(14) = ${last_atr:.2f}. "
        f"Per this plan, 1% risk on $10,000 = $100; since (entry − stop) = ${entry - stop:.2f}, "
        f"the number of shares = {int(100 / (entry - stop))}. "
        "Trading without a stop is like flying without a plan.",
    ))
    term_expander("stop-loss")


def _lesson_qullamaggie():
    st.subheader(_L("Qullamaggie Swing Stratejisi — 3 Zamansız Setup",
                    "Qullamaggie Swing Strategy — 3 Timeless Setups"))
    st.markdown(_L(
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
        "ortalama kırılana kadar** taşınır. Boğa piyasasında 10-20R'lik hareketler yakalanır.",
        "**Kristjan Kullamägi (Qullamaggie)** is a Swedish trader who went from a few thousand "
        "dollars to hundreds of millions through swing trading. His system rests on three simple "
        "but ruthlessly disciplined setups. The essence of his philosophy:\n\n"
        "> *Don't predict, react. No setup, no trade.*\n\n"
        "**The system's common backbone:**\n"
        "- Trade only the **strongest stocks**: the top 1–2% gainers over the last 1/3/6 months "
        "(a relative-strength filter)\n"
        "- Risk per trade: **0.25–1%** of the account — never more\n"
        "- Entry: the **opening range high** (a break of the first 1/5/60-minute candle's high)\n"
        "- Stop: **the day's low** — and never wider than ADR (average daily range)\n"
        "- Profit-taking: sell 1/3–1/2 of the position within 3–5 days, carry the rest **until the "
        "10/20-day average breaks**. In a bull market this captures 10–20R moves.",
    ))

    tab1, tab2, tab3 = st.tabs(["Setup 1: Breakout", "Setup 2: Episodic Pivot", "Setup 3: Parabolic"])
    with tab1:
        _qulla_breakout()
    with tab2:
        _qulla_ep()
    with tab3:
        _qulla_parabolic()

    st.divider()
    st.markdown(_L(
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
        "Kaybeden işlemde sabır ise en pahalı hatadır.",
        "**The real lessons from this strategy** (even more important than the setups):\n\n"
        "1. **Specialization**: Qullamaggie traded only these 3 setups for years. Someone who "
        "tries to do everything is good at nothing.\n"
        "2. **A trading journal**: for 7–8 years he archived screenshots of thousands of setups. "
        "His pattern-recognition ability came from that archive — repetition, not talent.\n"
        "3. **Asymmetry**: small, fixed risk (0.25–1%), open-ended gain (10–20R). Even at a 30–40% "
        "hit rate the system profits.\n"
        "4. **Market filter**: in a bear market most of these setups don't work — trade little, "
        "small size, or not at all in that period.\n"
        "5. **Patience is needed in two places**: while waiting for a setup, and while carrying a "
        "winner. Patience on a losing trade, however, is the most expensive mistake.",
    ))


def _qulla_breakout():
    st.markdown(_L(
        "**Mantık:** Güçlü yükselen hisse (%30-100+ hareket) soluklanır, 10/20 günlük "
        "ortalamaların üzerinde 2 hafta - 2 ay **dar bir bayrak/taban** kurar (bu sırada "
        "hacim kurur — VDU), sonra tabanın tepesini **yüksek hacimle** kırar. Giriş kırılım "
        "anında, stop günün dibinde.\n\n"
        "**Kontrol listesi:**\n"
        "1. Öncesinde güçlü hareket var mı (1-3 ayda %30+)?\n"
        "2. Konsolidasyon dar mı ve 10/20 MA üzerinde mi tutunuyor?\n"
        "3. Hacim konsolidasyonda kurudu mu, kırılımda patladı mı?\n"
        "4. Genel piyasa (QQQ/SPY) yükseliş trendinde mi?",
        "**The logic:** A strongly rising stock (a 30–100%+ move) catches its breath, builds a "
        "**tight flag/base** above the 10/20-day averages for 2 weeks to 2 months (volume dries "
        "up during this — VDU), then breaks the top of the base on **high volume**. Entry at the "
        "moment of the breakout, stop at the day's low.\n\n"
        "**Checklist:**\n"
        "1. Is there a strong prior move (30%+ in 1–3 months)?\n"
        "2. Is the consolidation tight and holding above the 10/20 MA?\n"
        "3. Did volume dry up in the consolidation and explode on the breakout?\n"
        "4. Is the broad market (QQQ/SPY) in an uptrend?",
    ))
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_breakout_setups(df):
            found.append((sym, e, df))
    if not found:
        st.info(_L("Mevcut verilerde kriterlere tam uyan breakout örneği bulunamadı.",
                   "No breakout example fully matching the criteria was found in the current data."))
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
    _annotate(fig, e["date"], e["price"], _L("KIRILIM", "BREAKOUT") + f"<br>{e['date']}", color="#3fb27f", ay=-50)
    _annotate(fig, e["date"], e["stop"], _L("Stop: günün dibi", "Stop: day's low") + f"<br>${e['stop']:.2f}",
              color="#d9534f", ay=45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"{sym} — {e['date']} tarihli GERÇEK breakout: öncesinde %{e['run_pct']} yükseliş, "
        f"sarı bölge = konsolidasyon (taban), noktalı çizgi = kırılan tepe (${e['cons_high']:.2f}). "
        "Kırılım günü hacim 50 günlük ortalamanın 1.5 katından fazlaydı.",
        f"{sym} — a REAL breakout dated {e['date']}: a {e['run_pct']}% prior run, the yellow zone = "
        f"consolidation (base), the dotted line = the broken high (${e['cons_high']:.2f}). On the "
        "breakout day volume was more than 1.5× the 50-day average.",
    ))
    if len(found) > 1:
        st.markdown(_L("**Veride bulunan diğer gerçek breakout örnekleri:**",
                       "**Other real breakout examples found in the data:**"))
        for s, ev, _ in found[:-1][-4:]:
            st.write(_L(
                f"- **{s}** — {ev['date']}: öncesinde %{ev['run_pct']} hareket, taban tepesi ${ev['cons_high']:.2f}",
                f"- **{s}** — {ev['date']}: a {ev['run_pct']}% prior move, base high ${ev['cons_high']:.2f}",
            ))


def _qulla_ep():
    st.markdown(_L(
        "**Mantık:** Beklenmedik büyük haber (kazanç sürprizi, FDA onayı, rehberlik artışı) "
        "hissenin kaderini bir gecede değiştirir. Kriterler:\n\n"
        "1. **%10+ gap-up** (bizim taramada %8+ kullanıldı)\n"
        "2. **Dev hacim** — açılıştan itibaren 2 kat üstü\n"
        "3. **Taze hareket** — hisse son 3-6 ayda zaten koşmuş OLMAMALI "
        "(herkesin bildiği hikâyede sürpriz kalmaz)\n"
        "4. Tercihen güçlü büyüme rakamları (EPS ve ciro)\n\n"
        "Giriş yine opening range high, stop günün dibi. EP'nin gücü: bu hareketler "
        "**aylarca sürebilir** — tek kazanç raporu 6 aylık trend başlatabilir. "
        "Qullamaggie'ye göre bu setup'ta ustalaşmak 4-8 kazanç sezonu (1-2 yıl) alır.",
        "**The logic:** Unexpected big news (an earnings surprise, FDA approval, raised guidance) "
        "changes a stock's fate overnight. Criteria:\n\n"
        "1. **A 10%+ gap-up** (our scan uses 8%+)\n"
        "2. **Huge volume** — 2×+ average from the open\n"
        "3. **A fresh move** — the stock must NOT have already run in the last 3–6 months "
        "(a story everyone knows holds no surprise)\n"
        "4. Preferably strong growth numbers (EPS and revenue)\n\n"
        "Entry is again the opening range high, stop the day's low. The EP's power: these moves "
        "**can last months** — a single earnings report can start a 6-month trend. Per "
        "Qullamaggie, mastering this setup takes 4–8 earnings seasons (1–2 years).",
    ))
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_episodic_pivots(df):
            found.append((sym, e, df))
    if not found:
        st.info(_L("Mevcut verilerde kriterlere uyan Episodic Pivot bulunamadı.",
                   "No Episodic Pivot matching the criteria was found in the current data."))
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
              "EPISODIC PIVOT" + f"<br>{e['date']}<br>" + _L(f"Gap %{e['gap_pct']}, hacim {e['volume_x']}x",
                                                             f"Gap {e['gap_pct']}%, volume {e['volume_x']}x"),
              color="#3fb27f", ay=-55)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"{sym} — {e['date']}: fiyat %{e['gap_pct']} gap ile açıldı, hacim ortalamanın "
        f"{e['volume_x']} katıydı. Grafikte gap sonrası aylarca ne olduğuna bak — EP'nin "
        "asıl kazandıranı gap günü değil, sonrasındaki trenddir. O tarihte hangi haberin "
        "çıktığını araştır (büyük ihtimalle kazanç açıklaması).",
        f"{sym} — {e['date']}: price opened with a {e['gap_pct']}% gap, volume was {e['volume_x']}× "
        "the average. Look at what happened for months after the gap — the EP's real payoff isn't "
        "the gap day but the trend that follows. Research what news came out that day (most likely "
        "an earnings release).",
    ))
    st.markdown(_L("**Veride bulunan diğer gerçek EP örnekleri:**", "**Other real EP examples found in the data:**"))
    for s, ev, _ in found[:-1][-4:]:
        st.write(_L(
            f"- **{s}** — {ev['date']}: gap %{ev['gap_pct']}, hacim {ev['volume_x']}x",
            f"- **{s}** — {ev['date']}: gap {ev['gap_pct']}%, volume {ev['volume_x']}x",
        ))


def _qulla_parabolic():
    st.markdown(_L(
        "**Mantık:** Bir hisse birkaç günde dikleşerek %50-100+ (küçük hisselerde %300-1000) "
        "yükselirse, art arda 3-5+ yeşil gün geldiyse — bu **parabolik aşırılık** "
        "sürdürülemez. Qullamaggie bu noktada dönüşü SHORT'lar:\n\n"
        "- Giriş: ilk kırmızı 5 dakikalık mum / opening range low\n"
        "- Stop: günün tepesi\n"
        "- Hedef: **10/20 günlük ortalamaya dönüş** (lastik bandın gevşemesi)\n"
        "- Tek intraday göstergesi: **VWAP**\n\n"
        "R:R bu setup'ta 5-10x'tir ama isabet oranı yüksektir. **Uyarı:** açığa satış "
        "sınırsız zarar riski taşır — bu setup en tecrübe isteyenidir. Bizim gibi "
        "öğrenenler için asıl değeri şudur: parabolik yükselişte ASLA alım kovalama.",
        "**The logic:** If a stock goes vertical, up 50–100%+ (300–1000% for small caps) in a few "
        "days with 3–5+ green days in a row — this **parabolic excess** is unsustainable. At this "
        "point Qullamaggie SHORTS the reversal:\n\n"
        "- Entry: the first red 5-minute candle / opening range low\n"
        "- Stop: the day's high\n"
        "- Target: **a return to the 10/20-day average** (the rubber band snapping back)\n"
        "- Only intraday indicator: **VWAP**\n\n"
        "R:R on this setup is 5–10x but the hit rate is high. **Warning:** short selling carries "
        "unlimited loss risk — this is the most experience-demanding setup. For learners like us "
        "its real value is: NEVER chase a parabolic rise.",
    ))
    found = []
    for sym in ["NVDA", "MU", "TSLA", "AAPL", "MSFT"]:
        df = _load_df(sym)
        for e in analysis.find_parabolic_moves(df):
            found.append((sym, e, df))
    if not found:
        st.info(_L(
            "Mevcut 5 büyük hissede son 5 yılda bu kriterlere (%30+/7 gün) uyan parabolik "
            "hareket bulunamadı — bu setup daha çok küçük, spekülatif hisselerde görülür. "
            "Bu da başlı başına bir ders: büyük şirketler nadiren parabolik olur.",
            "No parabolic move matching these criteria (30%+/7 days) was found in the 5 large "
            "stocks over the last 5 years — this setup shows up mostly in small, speculative "
            "stocks. That's a lesson in itself: large companies rarely go parabolic.",
        ))
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
              _L("PARABOLİK", "PARABOLIC") + f"<br>{e['date']}<br>" + _L(f"7 günde +%{e['gain_pct']}", f"+{e['gain_pct']}% in 7 days"),
              color="#d9534f", ay=-55)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(_L(
        f"{sym} — {e['date']}: 7 işlem gününde %{e['gain_pct']} yükseliş. Sonrasında "
        "fiyatın 10/20 günlük ortalamalara (mavi/turuncu) nasıl geri çekildiğine bak — "
        "parabolik hareketlerin 'yerçekimi' budur.",
        f"{sym} — {e['date']}: a {e['gain_pct']}% rise in 7 trading days. See how price then pulled "
        "back to the 10/20-day averages (blue/orange) — this is the 'gravity' of parabolic moves.",
    ))
    if len(found) > 1:
        st.markdown(_L("**Veride bulunan diğer parabolik hareketler:**", "**Other parabolic moves found in the data:**"))
        for s, ev, _ in found[:-1][-4:]:
            st.write(_L(
                f"- **{s}** — {ev['date']}: 7 günde +%{ev['gain_pct']}",
                f"- **{s}** — {ev['date']}: +{ev['gain_pct']}% in 7 days",
            ))
