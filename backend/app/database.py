"""
Veritabanı bağlantısı kurulumu.

SQLite kullanıyoruz çünkü: tek dosya, kurulum gerektirmez, başlangıç ve
öğrenme aşaması için yeterince hızlı. İleride çoklu kullanıcıya geçilirse
buradaki connection string'i PostgreSQL'e çevirmek yeterli olur — geri
kalan kod (ORM modelleri, sorgular) aynı kalır.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
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
