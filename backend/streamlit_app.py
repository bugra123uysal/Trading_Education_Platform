"""
Trading Eğitim Platformu — Streamlit giriş noktası.

Çalıştırmak için: `streamlit run streamlit_app.py` (backend/ klasöründe).

Neden tek bir Streamlit uygulaması: Önceki sürümde ayrı bir FastAPI
sunucusu + ayrı bir JavaScript frontend vardı (iki süreç, iki dil).
Artık her şey Python — Streamlit doğrudan app/ klasöründeki aynı
fonksiyonları (veri çekme, backtest motoru, quiz mantığı) çağırıyor,
ekstra bir API katmanına gerek kalmadı. Tek komutla tek uygulama çalışır.
"""
import streamlit as st

from app.database import Base, engine, session_scope
from app.data.seed_glossary import seed_glossary
from app.data.seed_quiz import seed_quiz
from ui import dashboard, quiz, glossary, replay, education

st.set_page_config(
    page_title="Trading Eğitim Platformu",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def init_database():
    """Tablo oluşturma ve başlangıç verisi yükleme — uygulama ömründe bir kez çalışır."""
    Base.metadata.create_all(bind=engine)
    with session_scope() as db:
        seed_glossary(db)
        seed_quiz(db)
    return True


init_database()

st.sidebar.title("Trading Eğitim Platformu")
st.sidebar.caption("Gerçek verilerle öğren, gerçek parayla riske girme.")

PAGES = {
    "Grafikler": dashboard,
    "Teknik Analiz Eğitimi": education,
    "Grafik Oynatıcı": replay,
    "Quiz": quiz,
    "Terim Sözlüğü": glossary,
}

selection = st.sidebar.radio("Sayfa", list(PAGES.keys()), label_visibility="collapsed")

PAGES[selection].render()
