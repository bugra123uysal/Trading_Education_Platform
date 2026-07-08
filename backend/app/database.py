"""
Veritabanı bağlantısı kurulumu.

SQLite kullanıyoruz çünkü: tek dosya, kurulum gerektirmez, başlangıç ve
öğrenme aşaması için yeterince hızlı. İleride çoklu kullanıcıya geçilirse
buradaki connection string'i PostgreSQL'e çevirmek yeterli olur — geri
kalan kod (ORM modelleri, sorgular) aynı kalır.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./data.db"

# check_same_thread=False: Streamlit her etkileşimde script'i yeniden
# çalıştırabilir ve iç mekanizması farklı thread'ler kullanabilir,
# SQLite varsayılan olarak buna izin vermez.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def session_scope():
    """`with session_scope() as db:` şeklinde kullanılır, sonunda otomatik kapanır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_content_schema() -> None:
    """İki dilli (i18n) sütunlar eski bir veritabanında yoksa içerik tablolarını tazeler.

    create_all mevcut tabloya sütun EKLEMEZ; bu yüzden eski şemalı bir
    data.db'de yeni `*_en` sütunları bulunmaz ve sorgular patlar. İçerik
    tabloları tohumdan yeniden üretilebilir olduğundan (glossary/quiz),
    şema eskiyse bunları düşürüp create_all + seed'in yeniden kurmasına
    izin veriyoruz. Sadece yerel geliştirme verisini etkiler; Streamlit
    Cloud'da disk zaten ephemeral. Quiz denemeleri (yerel ilerleme) sıfırlanır.
    """
    inspector = inspect(engine)
    if "glossary_terms" not in inspector.get_table_names():
        return  # tablo yok → create_all zaten güncel şemayı kuracak
    columns = {c["name"] for c in inspector.get_columns("glossary_terms")}
    if "term_en" in columns:
        return  # şema güncel
    stale = ["quiz_attempts", "quiz_questions", "glossary_terms", "user_progress"]
    with engine.begin() as conn:
        for table in stale:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
