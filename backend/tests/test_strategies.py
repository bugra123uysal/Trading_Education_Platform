"""
Strateji sinyal testleri.

MA crossover deterministik olduğu için tam sinyal dizisi assert edilir.
RSI eşik stratejisi için davranışsal invariantlar test edilir (aşırı
satımda giriş, düz seride giriş yok, çıktı domain'i {0,1}).
"""
from __future__ import annotations

import pandas as pd

from app.backtest.strategies import moving_average_crossover, rsi_threshold


def _df(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"close": [float(c) for c in closes]})


def test_ma_crossover_known_signals():
    """Bilinen seri için tam pozisyon dizisi doğrulanır."""
    df = _df([10, 10, 10, 10, 12, 14, 16, 18, 20, 15, 10, 8])
    pos = moving_average_crossover(df, fast_period=2, slow_period=3)
    assert list(pos) == [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0]


def test_ma_crossover_flat_series_no_position():
    """Düz seride fast asla slow'u geçmez → pozisyon tümüyle 0."""
    df = _df([10, 10, 10, 10, 10, 10])
    pos = moving_average_crossover(df, fast_period=2, slow_period=3)
    assert list(pos) == [0, 0, 0, 0, 0, 0]


def test_ma_crossover_warmup_bars_are_flat():
    """Rolling ortalama hesaplanamayan ilk barlarda pozisyon 0 olmalı."""
    df = _df([10, 20, 30, 40, 50])
    pos = moving_average_crossover(df, fast_period=2, slow_period=3)
    # slow_period=3 → ilk 2 bar NaN → pozisyon 0
    assert pos.iloc[0] == 0
    assert pos.iloc[1] == 0


def test_rsi_declining_series_enters_position(closes_declining):
    """Sürekli düşen seri RSI'ı aşırı satıma (buy_below altı) indirir → giriş."""
    df = _df(closes_declining)
    pos = rsi_threshold(df, rsi_period=3, buy_below=30, sell_above=70)
    assert pos.iloc[0] == 0  # başta pozisyon yok
    assert pos.iloc[-1] == 1  # düşüş sonunda pozisyona girilmiş


def test_rsi_flat_series_no_position():
    """Değişmeyen fiyatta RSI nötr (50) kalır → hiç giriş olmaz."""
    df = _df([50, 50, 50, 50, 50, 50, 50, 50])
    pos = rsi_threshold(df, rsi_period=3, buy_below=30, sell_above=70)
    assert list(pos) == [0] * 8


def test_rsi_output_domain_and_length(closes_declining):
    """Çıktı yalnızca {0,1} değerleri içermeli ve girdiyle aynı uzunlukta olmalı."""
    df = _df(closes_declining)
    pos = rsi_threshold(df, rsi_period=3)
    assert len(pos) == len(closes_declining)
    assert set(pos.unique()).issubset({0, 1})
