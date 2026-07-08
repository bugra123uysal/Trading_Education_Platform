"""
Backtest motoru testleri.

Beklenen değerler elle hesaplandı (conftest.py'deki fixture yorumlarına
bak). MA crossover fast=2/slow=3 ile kullanılıyor çünkü kısa warm-up
periyodu sinyalleri elle takip edilebilir kılıyor.
"""
from __future__ import annotations

import pytest

from app.backtest.engine import run_backtest


def test_single_trade_known_pnl(ohlcv_single_trade):
    """Bilinen seri tek bir +%25 trade üretmeli, sermaye 10k→12.5k olmalı."""
    result = run_backtest(
        ohlcv_single_trade, "ma_crossover", initial_capital=10000,
        fast_period=2, slow_period=3,
    )
    assert result["total_trades"] == 1
    assert result["win_rate"] == 100.0
    assert result["total_return_pct"] == 25.0
    assert result["final_capital"] == 12500.0

    trade = result["trades"][0]
    assert trade["entry_price"] == 12.0
    assert trade["exit_price"] == 15.0
    assert trade["profit_pct"] == 25.0
    assert trade["profit_abs"] == 2500.0


def test_two_trades_win_rate_and_metrics(ohlcv_two_trades):
    """Bir kazanç bir kayıp: win_rate %50, toplam getiri negatif."""
    result = run_backtest(
        ohlcv_two_trades, "ma_crossover", initial_capital=10000,
        fast_period=2, slow_period=3,
    )
    assert result["total_trades"] == 2
    assert result["win_rate"] == 50.0
    # T1 +%16.67, T2 -%23.08 → bileşik ~ -%10.26
    assert result["total_return_pct"] == pytest.approx(-10.26, abs=0.01)
    assert result["final_capital"] == pytest.approx(8974.36, abs=0.01)


def test_best_and_worst_trade_identification(ohlcv_two_trades):
    """best_trade en yüksek, worst_trade en düşük getirili trade olmalı."""
    result = run_backtest(
        ohlcv_two_trades, "ma_crossover", initial_capital=10000,
        fast_period=2, slow_period=3,
    )
    assert result["best_trade"]["profit_pct"] == pytest.approx(16.67, abs=0.01)
    assert result["worst_trade"]["profit_pct"] == pytest.approx(-23.08, abs=0.01)


def test_no_signal_returns_zero_trades(ohlcv_flat):
    """Düz seride hiç sinyal yok: 0 trade, nötr metrikler, sermaye değişmez."""
    result = run_backtest(
        ohlcv_flat, "ma_crossover", initial_capital=10000,
        fast_period=2, slow_period=3,
    )
    assert result["total_trades"] == 0
    assert result["win_rate"] == 0.0
    assert result["total_return_pct"] == 0.0
    assert result["final_capital"] == 10000.0
    assert result["best_trade"] is None
    assert result["worst_trade"] is None
    assert result["trades"] == []


def test_open_position_closed_on_last_bar(ohlcv_open_position):
    """Yükselerek biten seri: açık pozisyon son kapanışta kağıt üstünde kapanır."""
    result = run_backtest(
        ohlcv_open_position, "ma_crossover", initial_capital=10000,
        fast_period=2, slow_period=3,
    )
    assert result["total_trades"] == 1
    trade = result["trades"][0]
    assert trade["entry_price"] == 12.0
    assert trade["exit_price"] == 20.0  # son barın kapanışı
    assert trade["profit_pct"] == pytest.approx(66.67, abs=0.01)
    assert result["final_capital"] == pytest.approx(16666.67, abs=0.01)


def test_unknown_strategy_raises(ohlcv_single_trade):
    """Tanımsız strateji adı ValueError fırlatmalı."""
    with pytest.raises(ValueError, match="Bilinmeyen strateji"):
        run_backtest(ohlcv_single_trade, "does_not_exist")


def test_insufficient_data_raises():
    """5 bardan az veri backtest için reddedilmeli."""
    tiny = [{"date": "2024-01-01", "close": 10.0}] * 3
    with pytest.raises(ValueError, match="yeterli veri yok"):
        run_backtest(tiny, "ma_crossover", fast_period=2, slow_period=3)
