"""
yfinance üzerinden hisse verisi çekme + SQLite cache.

Neden cache: yfinance her istekte internet üzerinden veri çekiyor, bu
yavaş ve gereksiz (geçmiş veri zaten değişmiyor — sadece bugünün barı
değişebilir). Bu yüzden: bir sembolü ilk kez istediğimizde tüm geçmişi
çekip PriceBar tablosuna yazıyoruz. Sonraki isteklerde, son çekim
üzerinden CACHE_TTL'den az zaman geçtiyse direkt DB'den okuyoruz.

Dayanıklılık: yfinance geçici ağ/oran-sınırı hatalarına açık, bu yüzden
üstel geri çekilmeli (exponential backoff) yeniden deneme var. SQLite'a
yazma/okuma da (özellikle Streamlit Cloud'un tek yazıcılı ephemeral
diskinde) kilitlenebilir; kilit durumunda çökmek yerine mevcut veriye
ya da doğrudan yfinance'e düşülür.
"""
import logging
import time
from datetime import datetime, timedelta, timezone

import yfinance as yf
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Stock, PriceBar

logger = logging.getLogger("tep.fetcher")

CACHE_TTL = timedelta(hours=12)

# Yeniden deneme ayarları — harici retry kütüphanesi kullanmadan.
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0

# Demo amaçlı önceden tanımlı hisseler — kullanıcı dilediği sembolü de girebilir.
DEFAULT_SYMBOLS = {
    "MU": "Micron Technology",
    "NVDA": "NVIDIA Corporation",
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "MSFT": "Microsoft Corporation",
}

# Fetch tümüyle başarısız olduğunda kullanıcıya gösterilecek mesaj.
DATA_UNAVAILABLE_MESSAGE = "Veri şu an alınamıyor, lütfen biraz sonra tekrar deneyin."


def _is_cache_fresh(stock: Stock) -> bool:
    if stock.last_fetched_at is None:
        return False
    last = stock.last_fetched_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last < CACHE_TTL


def _fetch_from_yfinance(symbol: str):
    """yfinance'tan 5 yıllık günlük veri çeker; geçici hatalarda backoff ile yeniden dener."""
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5y", interval="1d")
            if hist.empty:
                # Boş sonuç geçici (oran sınırı) olabilir — yeniden dene.
                raise ValueError(f"'{symbol}' için boş veri döndü.")
            if attempt > 1:
                logger.info("yfinance %s: %d. denemede başarılı.", symbol, attempt)
            return hist
        except Exception as exc:  # ağ/oran-sınırı/boş veri — hepsi yeniden denenebilir
            last_error = exc
            if attempt < MAX_RETRIES:
                delay = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                logger.warning(
                    "yfinance %s çekme hatası (deneme %d/%d): %s — %.1fs sonra tekrar.",
                    symbol, attempt, MAX_RETRIES, exc, delay,
                )
                time.sleep(delay)
    logger.error("yfinance %s: %d denemenin hepsi başarısız. Son hata: %s",
                 symbol, MAX_RETRIES, last_error)
    raise ValueError(DATA_UNAVAILABLE_MESSAGE) from last_error


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


def _existing_bar_count(db: Session, stock_id: int) -> int:
    return db.query(PriceBar).filter(PriceBar.stock_id == stock_id).count()


def ensure_price_data(db: Session, symbol: str) -> Stock:
    """Belirtilen sembol için cache'i tazeler (gerekiyorsa yfinance'tan çeker).

    Cache tazeyse hiç ağ çağrısı yapılmaz. Çekme başarısız olur ama elde
    eski (bayat) cache varsa, çökmek yerine o cache ile devam edilir.
    Hem cache boş hem çekme başarısızsa ValueError yükseltilir.
    """
    stock = get_or_create_stock(db, symbol)

    if _is_cache_fresh(stock):
        return stock

    try:
        hist = _fetch_from_yfinance(stock.symbol)
    except ValueError:
        # Çekme başarısız — bayat da olsa cache varsa onunla devam et.
        if _existing_bar_count(db, stock.id) > 0:
            logger.warning("%s: çekme başarısız, mevcut (bayat) cache kullanılıyor.", symbol)
            return stock
        raise  # cache de boş → hatayı yukarı ilet

    try:
        # Mevcut barları silip yeniden yazmak, kısmi/eksik güncellemelerden
        # kaynaklanan tutarsızlıkları önlemenin en basit yolu.
        db.query(PriceBar).filter(PriceBar.stock_id == stock.id).delete()
        for index, row in hist.iterrows():
            db.add(PriceBar(
                stock_id=stock.id,
                date=index.strftime("%Y-%m-%d"),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
                volume=int(row["Volume"]),
            ))
        stock.last_fetched_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(stock)
    except OperationalError as exc:
        # DB kilidi (Streamlit Cloud tek yazıcı) — yazamadıysak bu isteği
        # çekilen veriyle karşılamak için rollback edip devam ediyoruz;
        # bir sonraki istek tekrar yazmayı dener.
        logger.warning("%s: SQLite yazma kilidi, cache güncellenemedi: %s", symbol, exc)
        db.rollback()
    except SQLAlchemyError as exc:
        logger.error("%s: cache yazma hatası: %s", symbol, exc)
        db.rollback()

    return stock


def get_candles(db: Session, symbol: str) -> list[PriceBar]:
    """Sembolün mum listesini döndürür (gerekirse çeker/cache'ler).

    Veri hiç sağlanamazsa (ağ başarısız + cache boş) ValueError yükseltir;
    çağıran katman (UI) bunu yakalayıp kullanıcıya durum bildirir.
    """
    stock = ensure_price_data(db, symbol)
    try:
        return (
            db.query(PriceBar)
            .filter(PriceBar.stock_id == stock.id)
            .order_by(PriceBar.date.asc())
            .all()
        )
    except OperationalError as exc:
        logger.warning("%s: cache okuma kilidi: %s", symbol, exc)
        raise ValueError(DATA_UNAVAILABLE_MESSAGE) from exc
