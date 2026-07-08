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

from app.database import Base, engine, ensure_content_schema, session_scope
from app.data.seed_glossary import seed_glossary
from app.data.seed_quiz import seed_quiz
from app.i18n import language_selector, t
from ui import dashboard, quiz, glossary, replay, education

st.set_page_config(
    page_title="Trading Education Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def init_database():
    """Tablo oluşturma ve başlangıç verisi yükleme — uygulama ömründe bir kez çalışır."""
    ensure_content_schema()  # eski şemayı (i18n sütunları eksik) tazele
    Base.metadata.create_all(bind=engine)
    with session_scope() as db:
        seed_glossary(db)
        seed_quiz(db)
    return True


init_database()

# Dil seçici en üstte — seçim st.session_state["lang"]'e yazılır ve tüm
# t() çağrıları bu turdan itibaren seçili dili kullanır.
language_selector()

st.sidebar.title(t("app_title"))
st.sidebar.caption(t("app_tagline"))

# (nav anahtarı, sayfa modülü) — etiketler seçili dile göre üretilir.
PAGES = [
    ("nav_charts", dashboard),
    ("nav_education", education),
    ("nav_replay", replay),
    ("nav_quiz", quiz),
    ("nav_glossary", glossary),
]
labels = [t(key) for key, _ in PAGES]

selection = st.sidebar.radio("nav", labels, label_visibility="collapsed")
module = PAGES[labels.index(selection)][1]
module.render()

# Disclaimer her sayfada görünür — eğitim aracı, yatırım tavsiyesi değil.
st.sidebar.divider()
st.sidebar.caption(t("disclaimer"))
