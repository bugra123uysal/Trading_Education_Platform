"""
Test fixture'ları — hepsi ağ erişimsiz, deterministik.

OHLCV serileri elle tasarlandı: MA crossover stratejisinin (fast=2,
slow=3) hangi barda sinyal üreteceği önceden hesaplanabilir. Böylece
testler "bilinen girdi → bilinen çıktı" ilkesiyle çalışır; yfinance'e
ya da gerçek piyasaya hiç dokunulmaz.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models  # noqa: F401 — tabloları Base.metadata'ya kaydeder


def _bars(closes: list[float]) -> list[dict]:
    """Kapanış listesini engine'in beklediği OHLCV dict listesine çevirir.

    Strateji ve engine yalnızca 'close' ve 'date' kullanır; diğer alanlar
    gerçekçilik için doldurulur.
    """
    out = []
    for i, c in enumerate(closes):
        out.append({
            "date": f"2024-01-{i + 1:02d}",
            "open": float(c),
            "high": float(c) + 1,
            "low": float(c) - 1,
            "close": float(c),
            "volume": 1_000_000,
        })
    return out


# --- Tek trade: +%25 kazançlı kesin senaryo ---
# closes=[10,10,10,10,12,14,16,18,20,15,10,8], fast=2/slow=3
# → pozisyon [0,0,0,0,1,1,1,1,1,0,0,0]
# → giriş i4 close=12, çıkış i9 close=15 → (15-12)/12 = +%25
@pytest.fixture
def ohlcv_single_trade() -> list[dict]:
    return _bars([10, 10, 10, 10, 12, 14, 16, 18, 20, 15, 10, 8])


# --- İki trade: bir kazanç bir kayıp ---
# closes=[10,10,10,12,14,16,18,14,10,10,13,11,10,10], fast=2/slow=3
# → pozisyon [0,0,0,1,1,1,1,0,0,0,1,1,0,0]
# → T1 giriş i3=12 çıkış i7=14 → +%16.67
# → T2 giriş i10=13 çıkış i12=10 → -%23.08
@pytest.fixture
def ohlcv_two_trades() -> list[dict]:
    return _bars([10, 10, 10, 12, 14, 16, 18, 14, 10, 10, 13, 11, 10, 10])


# --- Sinyalsiz: düz seri, fast asla slow'u geçmez → 0 trade ---
@pytest.fixture
def ohlcv_flat() -> list[dict]:
    return _bars([10, 10, 10, 10, 10, 10, 10, 10])


# --- Açık pozisyon: yükselerek biter, çıkış sinyali gelmez ---
# closes=[10,10,10,12,14,16,18,20] → pozisyon [0,0,0,1,1,1,1,1]
# → giriş i3=12, kağıt üstünde son barda (close=20) kapanır → +%66.67
@pytest.fixture
def ohlcv_open_position() -> list[dict]:
    return _bars([10, 10, 10, 12, 14, 16, 18, 20])


# --- Sürekli düşen seri: RSI aşırı satıma iner ---
@pytest.fixture
def closes_declining() -> list[float]:
    return [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40]


# --- Bellek içi veritabanı oturumu (dosya yok, ağ yok) ---
@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
