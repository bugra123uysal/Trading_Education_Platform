"""
ORM modelleri (veritabanı tabloları).

Tek kullanıcılı/local bir eğitim platformu olduğu için kullanıcı tablosu
yok — giriş sistemi yok, ilerleme tek bir "yerel kullanıcı" için tutuluyor.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Stock(Base):
    """Takip edilen hisse senetleri (örn. MU, NVDA)."""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    last_fetched_at = Column(DateTime, nullable=True)

    bars = relationship("PriceBar", back_populates="stock", cascade="all, delete-orphan")


class PriceBar(Base):
    """
    Günlük OHLCV mum verisi. yfinance'tan çekilip burada cache'lenir;
    bir sonraki istekte last_fetched_at TTL içindeyse tekrar API çağrısı
    yapılmaz, doğrudan buradan okunur — sayfa hızını bu sağlar.
    """
    __tablename__ = "price_bars"
    __table_args__ = (UniqueConstraint("stock_id", "date", name="uq_stock_date"),)

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(String(10), nullable=False)  # "YYYY-MM-DD" — lightweight-charts bu formatı bekler
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    stock = relationship("Stock", back_populates="bars")


class GlossaryTerm(Base):
    """
    Tıklanabilir terim sözlüğü. 'child_explanation' alanı kasıtlı olarak
    ayrı tutuldu: jargon yerine gerçek hayat benzetmesiyle anlatım burada.
    """
    __tablename__ = "glossary_terms"

    id = Column(Integer, primary_key=True)
    slug = Column(String(60), unique=True, nullable=False, index=True)
    term = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # örn: "temel", "teknik-analiz", "risk-yonetimi"
    short_definition = Column(String(200), nullable=False)
    child_explanation = Column(Text, nullable=False)
    example = Column(Text, nullable=True)


class QuizQuestion(Base):
    """
    Bilgi testi soruları. options JSON-string olarak saklanır (basit liste),
    ayrı bir tablo açmaya gerek yok çünkü şıklar soru dışında kullanılmıyor.
    """
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True)
    topic = Column(String(50), nullable=False)  # "temel-kavramlar" | "teknik-analiz" | "risk-yonetimi"
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # '["A", "B", "C", "D"]'
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)  # cevap doğru/yanlış fark etmeksizin gösterilecek açıklama
    related_glossary_slug = Column(String(60), nullable=True)


class QuizAttempt(Base):
    """Her quiz cevabının kaydı — ilerleme istatistikleri için kullanılır."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class UserProgress(Base):
    """Konu bazlı basit ilerleme sayacı (tek kullanıcı varsayımıyla)."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)
    topic = Column(String(50), unique=True, nullable=False)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
