"""
Teknik analiz eğitimi için "olay tespit" yardımcıları.

Buradaki fonksiyonlar gerçek fiyat verisini tarayıp eğitimde
gösterilecek olayları BULUR: altın kesişim hangi tarihte oldu,
en büyük gap nerede, çekiç mumu hangi gün oluştu vb. Böylece
eğitim sayfasındaki her işaret gerçekten o tarihte yaşanmış bir
olaydır — elle uydurulmuş örnek yoktur.
"""
import pandas as pd


# ---------- Temel göstergeler ----------

def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(window=period).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).fillna(50)


def bollinger(close: pd.Series, period: int = 20, num_std: float = 2.0):
    mid = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    return mid, mid + num_std * std, mid - num_std * std


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


# ---------- Olay tespitleri ----------

def find_ma_crosses(df: pd.DataFrame, fast: int = 50, slow: int = 200) -> list[dict]:
    """Altın (golden) ve ölüm (death) kesişimlerinin gerçek tarihlerini bulur."""
    f, s = sma(df["close"], fast), sma(df["close"], slow)
    above = (f > s).astype(int)
    change = above.diff()
    events = []
    for i in df.index[change == 1]:
        events.append({"date": df.loc[i, "date"], "type": "golden", "price": df.loc[i, "close"]})
    for i in df.index[change == -1]:
        events.append({"date": df.loc[i, "date"], "type": "death", "price": df.loc[i, "close"]})
    return sorted(events, key=lambda e: e["date"])


def find_swings(df: pd.DataFrame, window: int = 10) -> list[dict]:
    """
    Yerel tepe (swing high) ve dip (swing low) noktaları — piyasa yapısı
    (HH/HL/LH/LL) anlatımı için. window barlık pencerede en yüksek/düşük
    olan bar bir swing kabul edilir.
    """
    swings = []
    for i in range(window, len(df) - window):
        seg = df.iloc[i - window: i + window + 1]
        if df.loc[i, "high"] == seg["high"].max():
            swings.append({"date": df.loc[i, "date"], "price": df.loc[i, "high"], "kind": "high"})
        elif df.loc[i, "low"] == seg["low"].min():
            swings.append({"date": df.loc[i, "date"], "price": df.loc[i, "low"], "kind": "low"})
    return swings


def label_market_structure(swings: list[dict]) -> list[dict]:
    """Ardışık swinglere HH/HL/LH/LL etiketi ekler."""
    labeled = []
    last_high = None
    last_low = None
    for s in swings:
        item = dict(s)
        if s["kind"] == "high":
            if last_high is not None:
                item["label"] = "HH" if s["price"] > last_high else "LH"
            last_high = s["price"]
        else:
            if last_low is not None:
                item["label"] = "HL" if s["price"] > last_low else "LL"
            last_low = s["price"]
        labeled.append(item)
    return labeled


def find_support_resistance(df: pd.DataFrame, window: int = 10, tolerance: float = 0.02, min_touches: int = 2) -> list[dict]:
    """
    Fiyatın en az min_touches kez döndüğü yatay seviyeleri bulur.
    Swing noktalarını %tolerance yakınlığına göre gruplar.
    """
    swings = find_swings(df, window)
    levels: list[dict] = []
    for s in swings:
        placed = False
        for lv in levels:
            if abs(s["price"] - lv["price"]) / lv["price"] < tolerance:
                lv["touches"] += 1
                lv["dates"].append(s["date"])
                placed = True
                break
        if not placed:
            levels.append({"price": s["price"], "touches": 1, "dates": [s["date"]], "kind": s["kind"]})
    strong = [lv for lv in levels if lv["touches"] >= min_touches]
    return sorted(strong, key=lambda lv: -lv["touches"])[:4]


def find_gaps(df: pd.DataFrame, min_gap_pct: float = 4.0) -> list[dict]:
    """Bir önceki kapanışa göre %min_gap_pct üzeri boşlukla açılan günler."""
    gaps = []
    prev_close = df["close"].shift()
    gap_pct = (df["open"] - prev_close) / prev_close * 100
    for i in df.index[gap_pct.abs() >= min_gap_pct]:
        gaps.append({
            "date": df.loc[i, "date"],
            "gap_pct": round(float(gap_pct.loc[i]), 1),
            "price": df.loc[i, "open"],
            "direction": "up" if gap_pct.loc[i] > 0 else "down",
        })
    return gaps


def find_candle_patterns(df: pd.DataFrame) -> list[dict]:
    """
    Basit tek/çift mum formasyonlarını tespit eder: doji, çekiç (hammer),
    kayan yıldız (shooting star), yutan boğa/ayı (bullish/bearish engulfing).
    Ders için her türden en güncel birkaç örnek yeterlidir.
    """
    out = []
    for i in range(1, len(df)):
        o, h, lo, c = df.loc[i, ["open", "high", "low", "close"]]
        po, pc = df.loc[i - 1, ["open", "close"]]
        rng = h - lo
        if rng <= 0:
            continue
        body = abs(c - o)
        upper = h - max(o, c)
        lower = min(o, c) - lo
        date = df.loc[i, "date"]

        if body / rng < 0.1:
            out.append({"date": date, "pattern": "doji", "price": h})
        elif lower / rng > 0.6 and body / rng < 0.3:
            out.append({"date": date, "pattern": "hammer", "price": lo})
        elif upper / rng > 0.6 and body / rng < 0.3:
            out.append({"date": date, "pattern": "shooting_star", "price": h})
        elif c > o and pc < po and c > po and o < pc:
            out.append({"date": date, "pattern": "bullish_engulfing", "price": lo})
        elif c < o and pc > po and c < po and o > pc:
            out.append({"date": date, "pattern": "bearish_engulfing", "price": h})
    return out


def find_rsi_extremes(df: pd.DataFrame, period: int = 14) -> list[dict]:
    """RSI'ın 30 altına indiği / 70 üstüne çıktığı günleri bulur (bölge girişleri)."""
    r = rsi(df["close"], period)
    events = []
    was_oversold = False
    was_overbought = False
    for i in df.index:
        v = r.loc[i]
        if v < 30 and not was_oversold:
            events.append({"date": df.loc[i, "date"], "type": "oversold", "rsi": round(float(v), 1), "price": df.loc[i, "low"]})
        if v > 70 and not was_overbought:
            events.append({"date": df.loc[i, "date"], "type": "overbought", "rsi": round(float(v), 1), "price": df.loc[i, "high"]})
        was_oversold = v < 30
        was_overbought = v > 70
    return events


def biggest_swing(df: pd.DataFrame) -> dict:
    """Verideki en büyük dip→tepe hareketini bulur — Fibonacci dersi için."""
    low_idx = df["low"].idxmin()
    after = df.loc[low_idx:]
    high_idx = after["high"].idxmax()
    return {
        "low_date": df.loc[low_idx, "date"], "low": float(df.loc[low_idx, "low"]),
        "high_date": df.loc[high_idx, "date"], "high": float(df.loc[high_idx, "high"]),
    }


def fibonacci_levels(low: float, high: float) -> dict[str, float]:
    diff = high - low
    return {
        "0% (tepe)": high,
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff,
        "100% (dip)": low,
    }


# ---------- Qullamaggie setup tespitleri ----------

def find_breakout_setups(df: pd.DataFrame) -> list[dict]:
    """
    Qullamaggie Breakout setup'ı: (1) son 1-3 ayda %30+ güçlü yükseliş,
    (2) yükselen 10/20 günlük ortalamaların üzerinde 2 hafta - 2 ay
    konsolidasyon (dar aralık), (3) konsolidasyon tepesinin ortalama
    üstü hacimle kırıldığı gün. Gerçek geçmiş örnekleri bulur.
    """
    events = []
    ma20 = sma(df["close"], 20)
    vol_ma = df["volume"].rolling(50).mean()

    for i in range(80, len(df)):
        # (2) konsolidasyon: son 15 barın aralığı dar mı (< %18)?
        cons = df.iloc[i - 15: i]
        cons_high, cons_low = cons["high"].max(), cons["low"].min()
        if (cons_high - cons_low) / cons_low > 0.18:
            continue
        # 20 günlük MA yükseliyor ve fiyat üzerinde mi?
        if not (ma20.iloc[i - 1] > ma20.iloc[i - 6] and cons["close"].mean() > ma20.iloc[i - 1]):
            continue
        # (1) konsolidasyon öncesi güçlü yükseliş: ~3 ayda %25+
        base = df["close"].iloc[max(0, i - 75)]
        run_pct = (cons_low - base) / base * 100
        if run_pct < 25:
            continue
        # (3) kırılım günü: konsolidasyon tepesi aşıldı + hacim 1.3x üstü
        if df["close"].iloc[i] > cons_high and pd.notna(vol_ma.iloc[i]) and df["volume"].iloc[i] > vol_ma.iloc[i] * 1.3:
            events.append({
                "date": df["date"].iloc[i],
                "price": float(df["close"].iloc[i]),
                "cons_start": df["date"].iloc[i - 15],
                "cons_high": float(cons_high),
                "cons_low": float(cons_low),
                "run_pct": round(float(run_pct), 1),
                "stop": float(df["low"].iloc[i]),
                "index": i,
            })
    # Üst üste binen sinyalleri seyrelt: aynı aydan sadece ilkini al
    filtered = []
    for e in events:
        if not filtered or e["index"] - filtered[-1]["index"] > 20:
            filtered.append(e)
    return filtered


def find_episodic_pivots(df: pd.DataFrame, min_gap_pct: float = 8.0) -> list[dict]:
    """
    Episodic Pivot: %8+ gap-up + hacim patlaması (2x üstü) + öncesinde
    hissenin 3 ay boyunca güçlü rally YAPMAMIŞ olması (taze hareket).
    Genelde kazanç açıklaması / büyük haber günüdür.
    """
    events = []
    vol_ma = df["volume"].rolling(50).mean()
    prev_close = df["close"].shift()
    gap_pct = (df["open"] - prev_close) / prev_close * 100

    for i in range(65, len(df)):
        if gap_pct.iloc[i] < min_gap_pct:
            continue
        if pd.isna(vol_ma.iloc[i]) or df["volume"].iloc[i] < vol_ma.iloc[i] * 2:
            continue
        # Son 3 ayda zaten %40+ koşmuşsa "taze" değildir
        base = df["close"].iloc[i - 63]
        prior_run = (prev_close.iloc[i] - base) / base * 100
        if prior_run > 40:
            continue
        events.append({
            "date": df["date"].iloc[i],
            "gap_pct": round(float(gap_pct.iloc[i]), 1),
            "price": float(df["open"].iloc[i]),
            "volume_x": round(float(df["volume"].iloc[i] / vol_ma.iloc[i]), 1),
            "stop": float(df["low"].iloc[i]),
            "index": i,
        })
    return events


def find_parabolic_moves(df: pd.DataFrame, min_gain_pct: float = 30.0, days: int = 7) -> list[dict]:
    """
    Parabolic hareket: birkaç günde %30+ dikleşen yükseliş ve art arda
    yeşil günler — Qullamaggie'nin 'parabolic short' adayı dediği aşırılık.
    """
    events = []
    for i in range(days + 3, len(df)):
        gain = (df["close"].iloc[i] - df["close"].iloc[i - days]) / df["close"].iloc[i - days] * 100
        if gain < min_gain_pct:
            continue
        # Son 4 günün en az 3'ü yeşil mi?
        last4 = df.iloc[i - 3: i + 1]
        greens = (last4["close"] > last4["open"]).sum()
        if greens < 3:
            continue
        events.append({
            "date": df["date"].iloc[i],
            "gain_pct": round(float(gain), 1),
            "price": float(df["high"].iloc[i]),
            "index": i,
        })
    # ardışık günleri tekilleştir: her kümeden en yüksek kazançlıyı al
    filtered = []
    for e in events:
        if filtered and e["index"] - filtered[-1]["index"] <= 10:
            if e["gain_pct"] > filtered[-1]["gain_pct"]:
                filtered[-1] = e
        else:
            filtered.append(e)
    return filtered


def find_volume_dry_up(df: pd.DataFrame, lookback: int = 50, ratio: float = 0.5) -> list[dict]:
    """
    Hacim kuruması (VDU): hacmin 50 günlük ortalamasının yarısının altına
    düştüğü günler — konsolidasyonda patlama öncesi sessizlik sinyali.
    """
    vol_ma = df["volume"].rolling(window=lookback).mean()
    events = []
    for i in df.index:
        if pd.notna(vol_ma.loc[i]) and df.loc[i, "volume"] < vol_ma.loc[i] * ratio:
            events.append({"date": df.loc[i, "date"], "price": df.loc[i, "low"]})
    return events
