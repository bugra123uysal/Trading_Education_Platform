# Trading Eğitim Platformu

Gerçek ABD borsa verileriyle çalışan, backtest motoru + senaryo bazlı quizler +
tıklanabilir terim sözlüğü içeren, tamamen Python'da yazılmış bir trading
öğrenme platformu.

## Mimari

Tek bir Streamlit uygulaması — ayrı bir API sunucusu ya da JavaScript yok.
Her şey Python: veri çekme, backtest motoru, quiz mantığı ve arayüz aynı
süreçte çalışır.

- **Arayüz**: [Streamlit](https://streamlit.io) + [Plotly](https://plotly.com/python/) (mum grafikleri için).
- **Veri**: [yfinance](https://github.com/ranaroussi/yfinance) ile çekilir, SQLite'a cache'lenir (12 saatlik TTL).
- **Veritabanı**: SQLite (`backend/data.db`, otomatik oluşur) + SQLAlchemy ORM.

## Klasör Yapısı

```
backend/
  streamlit_app.py        # Giriş noktası — `streamlit run streamlit_app.py`
  app/
    database.py             # SQLite bağlantısı
    models.py                # ORM tabloları
    data/fetcher.py            # yfinance + cache mantığı
    data/seed_glossary.py      # Terim sözlüğü başlangıç verisi
    data/seed_quiz.py          # Quiz soruları başlangıç verisi
    backtest/strategies.py     # MA crossover, RSI threshold stratejileri
    backtest/engine.py         # İşlem simülasyonu + metrikler
    quiz/scenario.py           # Senaryo quiz üretimi
    quiz/grading.py            # Cevap değerlendirme + ilerleme kaydı
  ui/
    dashboard.py    # Grafikler sayfası
    backtest.py      # Backtest sayfası
    quiz.py           # Quiz sayfası (senaryo + bilgi testleri)
    glossary.py        # Terim sözlüğü sayfası
    common.py            # Paylaşılan yardımcılar (grafik çizimi, terim expander'ı)
  .streamlit/config.toml  # Koyu tema ayarları
```

## Kurulum ve Çalıştırma

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

Uygulama tarayıcıda otomatik açılır (varsayılan: http://localhost:8501).
İlk açılışta:
- SQLite tablolarını oluşturur (`data.db`)
- Terim sözlüğünü ve quiz sorularını veritabanına yükler (sadece tablo boşsa)
- Bir hisseye ilk kez bakıldığında yfinance'tan veri çeker, sonraki 12 saat
  boyunca DB'den okur (hızlı yükleme)

## Özellikler

1. **Grafikler**: Gerçek geçmiş hisse verisiyle mum grafiği (MU, NVDA, AAPL, TSLA, MSFT).
2. **Backtest**: MA crossover veya RSI threshold stratejisini seçilen tarih
   aralığında çalıştırıp kâr/zarar, kazanma oranı, en iyi/en kötü işlem gibi
   metrikleri ve alış/satış noktalarını grafik üzerinde gösterir.
3. **Quiz**:
   - *Senaryo Sorusu*: Gerçek bir hissenin geçmişinden rastgele bir an
     seçilir, "ne yapardın?" sorulur, sonra gerçekte ne olduğu gösterilir.
   - *Bilgi Testleri*: Temel kavramlar, teknik analiz, risk yönetimi
     konularında sorular — doğru ya da yanlış cevapta da açıklama gösterilir.
4. **Terim Sözlüğü**: Sade, çocuğa anlatır gibi yazılmış terim açıklamaları.
   Hem kendi sayfasında aranabilir/tıklanabilir liste halinde, hem de
   backtest/quiz sayfalarında ilgili terimler `st.expander` ile yerinde
   gösterilir (`ui/common.py` içindeki `term_expander` fonksiyonu).

## Yeni Terim/Soru Ekleme

- Terim eklemek için `backend/app/data/seed_glossary.py` içindeki `TERMS`
  listesine yeni bir `dict` ekleyin.
- Quiz sorusu eklemek için `backend/app/data/seed_quiz.py` içindeki
  `QUESTIONS` listesine ekleyin.
- Seed fonksiyonları sadece tablo **boşsa** çalışır. Yeni eklediğiniz
  verilerin yüklenmesi için `backend/data.db` dosyasını silip uygulamayı
  yeniden başlatmanız gerekir (geliştirme ortamında veri kaybı sorun değildir).

## Neden Bu Yapı

Önceki sürümde ayrı bir FastAPI sunucusu ve ayrı bir JavaScript frontend
vardı (iki süreç, iki dil). Python dışında bir dille uğraşmak istemediğiniz
için Streamlit'e geçtik: artık `ui/` klasöründeki her sayfa, `app/`
klasöründeki aynı Python fonksiyonlarını (örn. `run_backtest`,
`get_candles`) doğrudan çağırıyor — aradaki HTTP/JSON katmanı tamamen
kalktı. Tek komutla (`streamlit run streamlit_app.py`) tek bir uygulama
çalışır.
