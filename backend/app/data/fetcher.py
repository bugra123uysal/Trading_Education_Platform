"""
yfinance üzerinden hisse verisi çekme + SQLite cache.

Neden cache: yfinance her istekte internet üzerinden veri çekiyor, bu
yavaş ve gereksiz (geçmiş veri zaten değişmiyor — sadece bugünün barı
değişebilir). Bu yüzden: bir sembolü ilk kez istediğimizde tüm geçmişi
çekip PriceBar tablosuna yazıyoruz. Sonraki isteklerde, son çekim
üzerinden CACHE_TTL'den az zaman geçtiyse direkt DB'den okuyoruz.
"""
from datetime import datetime, timedelta, timezone

import yfinance as yf
from sqlalchemy.orm import Session

from app.models import Stock, PriceBar

CACHE_TTL = timedelta(hours=12)

# Demo amaçlı önceden tanımlı hisseler — kullanıcı dilediği sembolü de girebilir.
DEFAULT_SYMBOLS = {
    "MU": "Micron Technology",
    "NVDA": "NVIDIA Corporation",
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "MSFT": "Microsoft Corporation",
}


def _is_cache_fresh(stock: Stock) -> bool:
    if stock.last_fetched_at is None:
        return False
    last = stock.last_fetched_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last < CACHE_TTL


def _fetch_from_yfinance(symbol: str):
    ticker = yf.Ticker(symbol)
    # 5 yıllık günlük veri — backtest ve senaryo quizleri için yeterli derinlik
    hist = ticker.history(period="5y", interval="1d")
    if hist.empty:
        raise ValueError(f"'{symbol}' için veri bulunamadı. Sembolü kontrol edin.")
    return hist


def get_or_create_stock(db: Session, symbol: str) -> Stock:
    symbol = symbol.upper().strip()
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if stock is None:
        name = DEFAULT_SYMBOLS.get(symbol, symbol)
        stock = Stock(symbol=symbol, name=name)
        db.add(stock)
        db.commit()
        db.refresh(stock)
    return stock


def ensure_price_data(db: Session, symbol: str) -> Stock:
    """Belirtilen sembol için cache'i tazeler (gerekiyorsa yfinance'tan çeker)."""
    stock = get_or_create_stock(db, symbol)

    if _is_cache_fresh(stock):
        return stock

    hist = _fetch_from_yfinance(stock.symbol)

    # Mevcut barları silip yeniden yazmak, kısmi/eksik güncellemelerden
    # kaynaklanan tutarsızlıkları önlemenin en basit yolu — veri seti küçük
    # olduğu için performans sorunu yaratmaz.
    db.query(PriceBar).filter(PriceBar.stock_id == stock.id).delete()

    for index, row in hist.iterrows():
        bar = PriceBar(
            stock_id=stock.id,
            date=index.strftime("%Y-%m-%d"),
            open=round(float(row["Open"]), 2),
            high=round(float(row["High"]), 2),
            low=round(float(row["Low"]), 2),
            close=round(float(row["Close"]), 2),
            volume=int(row["Volume"]),
        )
        db.add(bar)

    stock.last_fetched_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(stock)
    return stock


def get_candles(db: Session, symbol: str) -> list[PriceBar]:
    stock = ensure_price_data(db, symbol)
    return (
        db.query(PriceBar)
        .filter(PriceBar.stock_id == stock.id)
        .order_by(PriceBar.date.asc())
        .all()
    )
