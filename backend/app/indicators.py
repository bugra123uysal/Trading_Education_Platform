"""
Teknik indikatör hesaplamaları.

İki indikatör, kullanıcının paylaştığı Pine Script versiyonlarının
mantığını birebir Python/pandas'a çeviriyor:

1. "3 EMAS" — 50/100/200 günlük üstel hareketli ortalama (fiyat grafiği
   üzerine bindirilir).
2. "Dollar Volume (Qullamaggie Style)" — kapanış fiyatı × hacim (yani o
   günkü dolar cinsinden işlem büyüklüğü) ve bunun 50 günlük ortalaması.
   Sadece hisse adedi yerine dolar büyüklüğüne bakmak, düşük fiyatlı ama
   yüksek hacimli hisselerle yüksek fiyatlı hisseleri adil kıyaslamayı
   sağlar.
"""
import pandas as pd


def add_ema_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Pine'daki ema(src, len) karşılığı: pandas ewm (span bazlı üstel ortalama)."""
    df = df.copy()
    df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema_100"] = df["close"].ewm(span=100, adjust=False).mean()
    df["ema_200"] = df["close"].ewm(span=200, adjust=False).mean()
    return df


def add_dollar_volume_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Pine'daki dollarVolume = close * volume ve onun 50 günlük SMA'sı."""
    df = df.copy()
    df["dollar_volume"] = df["close"] * df["volume"]
    df["dollar_volume_ma50"] = df["dollar_volume"].rolling(window=50).mean()
    return df


def with_indicators(bars: list[dict]) -> pd.DataFrame:
    """bars: [{date, open, high, low, close, volume}, ...] -> indikatörlü DataFrame."""
    df = pd.DataFrame(bars).reset_index(drop=True)
    df = add_ema_columns(df)
    df = add_dollar_volume_columns(df)
    return df
