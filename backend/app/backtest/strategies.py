"""
Strateji tanımları.

Her strateji fonksiyonu bir pandas DataFrame (en az 'close' sütunu) alır
ve günlük "pozisyon" serisi döndürür: 1 = o gün hisseyi elimizde tut
(long), 0 = elimizde tutma (flat/nakit). Engine bu seriyi okuyup
0 -> 1 geçişlerini "alış", 1 -> 0 geçişlerini "satış" olarak yorumlar.

Bu basit "pozisyonda mıyım değil miyim" modeli kaldıraçsız, tek
pozisyonluk bir trader'ı simüle eder — eğitim amacına uygun, gerçek
borsa mekaniğinin (kısmi alım, kaldıraç vb.) karmaşıklığına girmeden
strateji mantığını net gösterir.
"""
import pandas as pd


def moving_average_crossover(df: pd.DataFrame, fast_period: int = 20, slow_period: int = 50) -> pd.Series:
    """
    Hareketli ortalama kesişimi: kısa vadeli ortalama (fast) uzun vadeli
    ortalamayı (slow) yukarı keserse "yükseliş trendi başlıyor" sinyali
    alıp pozisyona gireriz; aşağı keserse pozisyondan çıkarız.
    """
    fast_ma = df["close"].rolling(window=fast_period).mean()
    slow_ma = df["close"].rolling(window=slow_period).mean()
    position = (fast_ma > slow_ma).astype(int)
    # rolling ortalama henüz hesaplanamayan ilk barlarda pozisyon almayız
    position[fast_ma.isna() | slow_ma.isna()] = 0
    return position


def _compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # ilk barlarda nötr değer


def rsi_threshold(df: pd.DataFrame, rsi_period: int = 14, buy_below: float = 30, sell_above: float = 70) -> pd.Series:
    """
    RSI eşik stratejisi: RSI 'aşırı satım' bölgesine (buy_below altı)
    düşünce ucuzladığını varsayıp alırız; 'aşırı alım' bölgesine
    (sell_above üstü) çıkınca pahalandığını varsayıp satarız.
    """
    rsi = _compute_rsi(df["close"], rsi_period)

    position = pd.Series(0, index=df.index)
    in_position = False
    for i in range(len(df)):
        if not in_position and rsi.iloc[i] < buy_below:
            in_position = True
        elif in_position and rsi.iloc[i] > sell_above:
            in_position = False
        position.iloc[i] = 1 if in_position else 0
    return position


STRATEGIES = {
    "ma_crossover": moving_average_crossover,
    "rsi_threshold": rsi_threshold,
}
