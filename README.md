# 🎓 Trading Education Platform

Live demo: https://trade-egitim.streamlit.app/

<img width="1140" height="487" alt="Ekran görüntüsü 2026-07-02 143513" src="https://github.com/user-attachments/assets/adcbf26b-21b2-4de6-9db4-4d541f344ea0" />
<img width="1103" height="462" alt="Ekran görüntüsü 2026-07-02 143503" src="https://github.com/user-attachments/assets/14e7f2b4-5cf7-41d8-8867-bca6cb3322ee" />
<img width="1178" height="420" alt="Ekran görüntüsü 2026-07-02 143444" src="https://github.com/user-attachments/assets/64b1a19f-6f07-4f27-a579-e6bc939783c9" />
<img width="1152" height="453" alt="Ekran görüntüsü 2026-07-02 143433" src="https://github.com/user-attachments/assets/cd61c8d4-7a37-4987-a602-4d280e542d22" />
<img width="1680" height="495" alt="Ekran görüntüsü 2026-07-02 143418" src="https://github.com/user-attachments/assets/5a2505cb-669e-448a-a4ec-f7466353a479" />
<img width="1902" height="743" alt="Ekran görüntüsü 2026-07-02 143327" src="https://github.com/user-attachments/assets/98011d1d-ec35-4d88-a62d-35b7ec7cfc14" />
<img width="1204" height="765" alt="Ekran görüntüsü 2026-07-02 143524" src="https://github.com/user-attachments/assets/8114f965-9d21-4b04-8407-b50a152cdcfd" />


**English** | [Türkçe](#-türkçe)

Problem: After learning trading concepts, beginners need a safe environment to practice. Existing solutions rarely focus on education, making it difficult to gain experience without risking real capital.

A trading learning platform built entirely in Python, powered by **real US market data**. It combines a backtesting engine, scenario-based quizzes, and a clickable glossary in a single Streamlit application.

> *Learn with real data — without risking real money.*

## 🏗️ Architecture

One Streamlit app, one process, one language. No separate API server, no JavaScript. The UI calls the same Python functions (`run_backtest`, `get_candles`, …) directly — no HTTP/JSON layer in between.

- **UI**: [Streamlit](https://streamlit.io) + [Plotly](https://plotly.com/python/) (candlestick charts)
- **Data**: fetched via [yfinance](https://github.com/ranaroussi/yfinance), cached in SQLite with a 12-hour TTL
- **Database**: SQLite (`backend/data.db`, auto-created) + SQLAlchemy ORM

## 📁 Project Structure

```
backend/
  streamlit_app.py           # Entry point — `streamlit run streamlit_app.py`
  app/
    database.py              # SQLite connection
    models.py                # ORM tables
    indicators.py            # EMA, dollar-volume columns
    data/fetcher.py          # yfinance + caching logic
    data/seed_glossary.py    # Glossary seed data
    data/seed_quiz.py        # Quiz question seed data
    backtest/strategies.py   # MA crossover, RSI threshold strategies
    backtest/engine.py       # Trade simulation + performance metrics
    quiz/scenario.py         # Scenario quiz generation
    quiz/grading.py          # Answer grading + progress tracking
  ui/
    dashboard.py             # Charts page
    backtest.py              # Backtest page
    quiz.py                  # Quiz page (scenario + knowledge tests)
    glossary.py              # Glossary page
    common.py                # Shared helpers (chart rendering, term expanders)
  .streamlit/config.toml     # Dark theme settings
```

## 🛠️ Features

1. **Charts** — Candlestick charts with real historical data (MU, NVDA, AAPL, TSLA, MSFT)
2. **Backtesting** — Run an MA crossover or RSI threshold strategy over a chosen date range; get profit/loss, win rate, best/worst trade, and buy/sell markers plotted on the chart
3. **Quizzes**
   - *Scenario questions*: a random moment is picked from a real stock's history — "What would you do?" — then the actual outcome is revealed
   - *Knowledge tests*: fundamentals, technical analysis, and risk management, with explanations shown for both correct and incorrect answers
4. **Glossary** — Plain-language term explanations, searchable on its own page and embedded contextually (via `st.expander`) on the backtest and quiz pages

## 🚀 Setup & Run

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app opens automatically in your browser (default: http://localhost:8501). On first launch it creates the SQLite tables, seeds the glossary and quiz questions (only if tables are empty), and caches yfinance data for 12 hours after the first lookup.

## ➕ Adding Terms & Questions

- Add a term: append a `dict` to the `TERMS` list in `backend/app/data/seed_glossary.py`
- Add a quiz question: append to the `QUESTIONS` list in `backend/app/data/seed_quiz.py`
- Seed functions run only when tables are **empty** — delete `backend/data.db` and restart to load new entries (data loss is fine in development)

## 🤔 Why This Architecture

An earlier version used a separate FastAPI server plus a JavaScript frontend — two processes, two languages. Migrating to Streamlit removed the entire HTTP/JSON layer: every page in `ui/` now calls the same Python functions in `app/` directly, and a single command runs the whole application.

## ⚠️ Disclaimer

Educational tool only. Not investment advice.

---

# 🇹🇷 Türkçe
canlı demo: https://trade-egitim.streamlit.app/

Sorun: Alım-satım kavramlarını öğrendikten sonra, yeni başlayanların pratik yapabilecekleri güvenli bir ortama ihtiyaçları vardır. Mevcut çözümler nadiren eğitime odaklandığından, gerçek sermayeyi riske atmadan deneyim kazanmak zorlaşmaktadır.

Gerçek ABD borsa verileriyle çalışan, tamamen Python'da yazılmış bir trading öğrenme platformu. Backtest motoru, senaryo bazlı quizler ve tıklanabilir terim sözlüğünü tek bir Streamlit uygulamasında birleştirir.

> *Gerçek verilerle öğren, gerçek parayla riske girme.*

## 🏗️ Mimari

Tek Streamlit uygulaması, tek süreç, tek dil. Ayrı API sunucusu yok, JavaScript yok. Arayüz, aynı Python fonksiyonlarını (`run_backtest`, `get_candles`, …) doğrudan çağırır — arada HTTP/JSON katmanı yoktur.

- **Arayüz**: [Streamlit](https://streamlit.io) + [Plotly](https://plotly.com/python/) (mum grafikleri)
- **Veri**: [yfinance](https://github.com/ranaroussi/yfinance) ile çekilir, SQLite'a cache'lenir (12 saatlik TTL)
- **Veritabanı**: SQLite (`backend/data.db`, otomatik oluşur) + SQLAlchemy ORM

## 🛠️ Özellikler

1. **Grafikler** — Gerçek geçmiş veriyle mum grafikleri (MU, NVDA, AAPL, TSLA, MSFT)
2. **Backtest** — Seçilen tarih aralığında MA crossover veya RSI threshold stratejisini çalıştırır; kâr/zarar, kazanma oranı, en iyi/en kötü işlem metriklerini ve alış/satış noktalarını grafik üzerinde gösterir
3. **Quiz**
   - *Senaryo sorusu*: Gerçek bir hissenin geçmişinden rastgele bir an seçilir — "Ne yapardın?" — sonra gerçekte ne olduğu gösterilir
   - *Bilgi testleri*: Temel kavramlar, teknik analiz ve risk yönetimi; doğru ya da yanlış cevapta da açıklama gösterilir
4. **Terim Sözlüğü** — Sade dille yazılmış terim açıklamaları; hem kendi sayfasında aranabilir liste olarak, hem de backtest/quiz sayfalarında bağlam içinde (`st.expander` ile) gösterilir

## 🚀 Kurulum ve Çalıştırma

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

Uygulama tarayıcıda otomatik açılır (varsayılan: http://localhost:8501). İlk açılışta SQLite tablolarını oluşturur, sözlük ve quiz verilerini yükler (sadece tablolar boşsa) ve ilk bakılan hissenin verisini 12 saat boyunca cache'ler.

## ➕ Yeni Terim / Soru Ekleme

- Terim: `backend/app/data/seed_glossary.py` içindeki `TERMS` listesine yeni `dict` ekleyin
- Quiz sorusu: `backend/app/data/seed_quiz.py` içindeki `QUESTIONS` listesine ekleyin
- Seed fonksiyonları sadece tablo **boşsa** çalışır — yeni verilerin yüklenmesi için `backend/data.db` dosyasını silip uygulamayı yeniden başlatın (geliştirme ortamında veri kaybı sorun değildir)

## 🤔 Neden Bu Mimari

Önceki sürümde ayrı bir FastAPI sunucusu ve JavaScript frontend vardı — iki süreç, iki dil. Streamlit'e geçişle HTTP/JSON katmanı tamamen kalktı: `ui/` klasöründeki her sayfa, `app/` içindeki aynı Python fonksiyonlarını doğrudan çağırıyor ve tek komut tüm uygulamayı çalıştırıyor.

## ⚠️ Uyarı

Yalnızca eğitim amaçlıdır. Yatırım tavsiyesi değildir.

---

## 👤 Developer / Geliştirici

**Mesut Buğra Uysal**
[GitHub](https://github.com/bugra123uysal) · [LinkedIn](https://www.linkedin.com/in/mesut-bu%C4%9Fra-uysal-16a1bb288/)
