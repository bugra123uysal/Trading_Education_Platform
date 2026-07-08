"""
Basit iki dilli (TR/EN) metin altyapısı.

Neden ayrı modül: UI metinleri tek bir sözlükte toplanır, sayfalar
`t("anahtar")` ile çağırır. Seçili dil st.session_state'te tutulur,
kullanıcı sidebar'daki seçiciyle anında değiştirir. Harici i18n
kütüphanesine gerek yok — proje küçük ve tek süreçli.

Kapsam: arayüz çerçevesi (menü, başlıklar, butonlar, metrikler,
disclaimer, dashboard, grafik oynatıcı). Derinlemesine eğitim içeriği
(ders anlatımları, sözlük tanımları, quiz soruları) şimdilik Türkçe;
bunlar veri/içerik katmanında ayrıca genişletilebilir.
"""
from __future__ import annotations

import streamlit as st

LANGUAGES = {"tr": "🇹🇷 Türkçe", "en": "🇬🇧 English"}
DEFAULT_LANG = "tr"

# key -> {"tr": ..., "en": ...}
_STRINGS: dict[str, dict[str, str]] = {
    # --- Sidebar / genel ---
    "app_title": {"tr": "Trading Eğitim Platformu", "en": "Trading Education Platform"},
    "app_tagline": {
        "tr": "Gerçek verilerle öğren, gerçek parayla riske girme.",
        "en": "Learn with real data — without risking real money.",
    },
    "language_label": {"tr": "Dil / Language", "en": "Language / Dil"},
    "disclaimer": {
        "tr": "⚠️ Bu uygulama yalnızca eğitim amaçlıdır ve yatırım tavsiyesi değildir. "
              "Geçmiş performans gelecekteki sonuçları garanti etmez.",
        "en": "⚠️ This app is for educational purposes only and is not investment advice. "
              "Past performance does not guarantee future results.",
    },
    # --- Sayfa adları (menü) ---
    "nav_charts": {"tr": "Grafikler", "en": "Charts"},
    "nav_education": {"tr": "Teknik Analiz Eğitimi", "en": "Technical Analysis"},
    "nav_replay": {"tr": "Grafik Oynatıcı", "en": "Chart Replay"},
    "nav_quiz": {"tr": "Quiz", "en": "Quiz"},
    "nav_glossary": {"tr": "Terim Sözlüğü", "en": "Glossary"},
    # --- Ortak ---
    "symbol_label": {"tr": "Hisse Sembolü", "en": "Stock Symbol"},
    "data_unavailable": {
        "tr": "Veri şu an alınamıyor, lütfen biraz sonra tekrar deneyin.",
        "en": "Data is unavailable right now, please try again shortly.",
    },
    "loading": {"tr": "{symbol} verisi yükleniyor…", "en": "Loading {symbol} data…"},
    # --- Dashboard ---
    "dash_title": {"tr": "Hisse Senedi Grafikleri", "en": "Stock Charts"},
    "dash_intro": {
        "tr": "Gerçek geçmiş veriler üzerinde mum grafiklerini inceleyin.",
        "en": "Explore candlestick charts on real historical data.",
    },
    "dash_last_close": {"tr": "Son Kapanış", "en": "Last Close"},
    "dash_total_change": {
        "tr": "Toplam Değişim (gösterilen aralıkta)",
        "en": "Total Change (shown range)",
    },
    "dash_bar_count": {"tr": "Bar Sayısı", "en": "Bar Count"},
    # --- Replay ---
    "replay_title": {"tr": "Grafik Oynatıcı (Replay)", "en": "Chart Replay"},
    "replay_intro": {
        "tr": "Grafiği geçmişte bir tarihe geri sar, sonra gün gün oynat — geleceği "
              "bilmeden fiyatın nasıl aktığını izle. TradingView'daki Bar Replay'in "
              "eğitim amaçlı basit halidir.",
        "en": "Rewind the chart to a past date, then play it forward day by day — watch "
              "how price unfolds without knowing the future. An educational take on "
              "TradingView's Bar Replay.",
    },
    "replay_speed": {"tr": "Oynatma Hızı", "en": "Playback Speed"},
    "replay_speed_slow": {"tr": "Yavaş (0.5 sn/gün)", "en": "Slow (0.5s/day)"},
    "replay_speed_normal": {"tr": "Normal (0.25 sn/gün)", "en": "Normal (0.25s/day)"},
    "replay_speed_fast": {"tr": "Hızlı (0.1 sn/gün)", "en": "Fast (0.1s/day)"},
    "replay_rewind_to": {"tr": "Grafiği bu tarihe geri sar:", "en": "Rewind chart to:"},
    "replay_rewind_btn": {"tr": "⏮ Bu Tarihe Geri Sar", "en": "⏮ Rewind Here"},
    "replay_hint_start": {
        "tr": "Yukarıdan bir tarih seçip 'Geri Sar' butonuna bas — grafik o güne dönecek.",
        "en": "Pick a date above and hit 'Rewind' — the chart jumps to that day.",
    },
    "replay_step1": {"tr": "+1 gün", "en": "+1 day"},
    "replay_step5": {"tr": "+5 gün", "en": "+5 days"},
    "replay_play20": {"tr": "▶ 20 gün oynat", "en": "▶ Play 20 days"},
    "replay_play_all": {"tr": "▶▶ Sona kadar", "en": "▶▶ To the end"},
    "replay_reset": {"tr": "⏮ Başa dön", "en": "⏮ Reset"},
    "replay_current_date": {"tr": "Şu Anki Tarih", "en": "Current Date"},
    "replay_close": {"tr": "Kapanış", "en": "Close"},
    "replay_change_since": {
        "tr": "{pct}% (geri sarma noktasından beri)",
        "en": "{pct}% (since rewind point)",
    },
    "replay_days_left": {"tr": "Kalan Gün", "en": "Days Left"},
    "replay_rewind_point": {"tr": "Geri sarma noktası", "en": "Rewind point"},
    "replay_no_days": {
        "tr": "Grafik zaten en güncel tarihte — oynatılacak gün kalmadı.",
        "en": "Chart is already at the latest date — no days left to play.",
    },
    "replay_played": {
        "tr": "{n} gün oynatıldı. Şu an {date} tarihindesin. "
              "Devam etmek için tekrar oynat ya da adım butonlarını kullan.",
        "en": "Played {n} days. You're now at {date}. "
              "Play again or use the step buttons to continue.",
    },
    "replay_tip": {
        "tr": "İpucu: Bir tarihte dur, kendine 'buradan sonra ne olur?' diye sor, tahminini "
              "yap, sonra oynat ve gerçekle karşılaştır. Bu alıştırmayı farklı hisse ve "
              "dönemlerde tekrarlamak, grafik okuma refleksini geliştirir.",
        "en": "Tip: Pause at a date, ask yourself 'what happens next?', make your guess, "
              "then play and compare with reality. Repeating this across different stocks "
              "and periods sharpens your chart-reading instinct.",
    },
    # --- Glossary ---
    "glossary_title": {"tr": "Terim Sözlüğü", "en": "Glossary"},
    "glossary_intro": {
        "tr": "Trading'de sık karşılaşacağın terimleri burada sade, gündelik bir dille açıklıyoruz.",
        "en": "Plain-language explanations of terms you'll frequently meet in trading.",
    },
    "glossary_search": {"tr": "Terim Ara", "en": "Search terms"},
    "glossary_search_ph": {
        "tr": "örn: stop-loss, RSI, hacim...",
        "en": "e.g. stop-loss, RSI, volume...",
    },
    "glossary_no_match": {
        "tr": "Aramanızla eşleşen bir terim bulunamadı.",
        "en": "No term matched your search.",
    },
    # --- Kategori etiketleri ---
    "cat_temel": {"tr": "Temel Kavram", "en": "Fundamentals"},
    "cat_teknik-analiz": {"tr": "Teknik Analiz", "en": "Technical Analysis"},
    "cat_risk-yonetimi": {"tr": "Risk Yönetimi", "en": "Risk Management"},
    # --- term_expander öntakısı ---
    "term_prefix": {"tr": "Terim", "en": "Term"},
    # --- Quiz genel ---
    "quiz_title": {"tr": "Quiz", "en": "Quiz"},
    "quiz_intro": {
        "tr": "Bilgini test et ya da gerçek bir piyasa senaryosunda ne yapacağına karar ver.",
        "en": "Test your knowledge, or decide what you'd do in a real market scenario.",
    },
    "quiz_tab_scenario": {"tr": "Senaryo Sorusu", "en": "Scenario Question"},
    "topic_temel-kavramlar": {"tr": "Temel Kavramlar", "en": "Fundamentals"},
    "topic_teknik-analiz": {"tr": "Teknik Analiz", "en": "Technical Analysis"},
    "topic_risk-yonetimi": {"tr": "Risk Yönetimi", "en": "Risk Management"},
    "topic_grafik-okuma": {"tr": "Grafik Okuma", "en": "Chart Reading"},
    "quiz_options": {"tr": "Seçenekler", "en": "Options"},
    "quiz_answer_btn": {"tr": "Cevapla", "en": "Answer"},
    "quiz_correct": {"tr": "Doğru!", "en": "Correct!"},
    "quiz_wrong": {"tr": "Yanlış. Doğru cevap: {answer}", "en": "Wrong. Correct answer: {answer}"},
    "quiz_next": {"tr": "Sonraki Soru", "en": "Next Question"},
    "quiz_finish": {"tr": "Bitir", "en": "Finish"},
    "quiz_question_n": {"tr": "Soru {i} / {total}", "en": "Question {i} / {total}"},
    "quiz_done": {"tr": "Tamamlandı", "en": "Completed"},
    "quiz_score": {
        "tr": "{total} sorudan {correct} tanesini doğru bildin.",
        "en": "You got {correct} out of {total} correct.",
    },
    "quiz_restart": {"tr": "Tekrar Başla", "en": "Restart"},
    "quiz_no_questions": {"tr": "Bu konuda henüz soru yok.", "en": "No questions in this topic yet."},
    # --- Eğitim (education) sayfa çerçevesi ---
    "edu_title": {"tr": "Teknik Analiz Eğitimi", "en": "Technical Analysis Education"},
    "edu_intro": {
        "tr": "Her ders, kavramı önce sade bir dille anlatır; sonra **gerçek bir hisse "
              "grafiğinde, gerçek tarihiyle** örneğini gösterir. Grafiklerdeki tüm işaretler "
              "geçmiş veriden otomatik tespit edilmiştir — kurgu örnek yoktur. "
              "Öğrendiklerini Quiz sayfasındaki **Grafik Okuma** testiyle sınayabilirsin.",
        "en": "Each lesson first explains a concept in plain language, then shows an example "
              "**on a real stock chart with its real date**. Every marker on the charts is "
              "detected automatically from historical data — no fabricated examples. Test what "
              "you learn with the **Chart Reading** quiz.",
    },
    "edu_select_lesson": {"tr": "Ders seç", "en": "Select a lesson"},
}


def get_lang() -> str:
    """Seçili dil kodunu döndürür (varsayılan: tr)."""
    return st.session_state.get("lang", DEFAULT_LANG)


def t(key: str, **kwargs: object) -> str:
    """Anahtarın seçili dildeki metnini döndürür; {placeholder} varsa doldurur."""
    entry = _STRINGS.get(key, {})
    text = entry.get(get_lang()) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def language_selector() -> None:
    """Sidebar'a TR/EN dil seçici yerleştirir; seçim session_state'e yazılır."""
    codes = list(LANGUAGES.keys())
    current = get_lang()
    choice = st.sidebar.radio(
        t("language_label"),
        options=codes,
        index=codes.index(current) if current in codes else 0,
        format_func=lambda c: LANGUAGES[c],
        horizontal=True,
        key="lang",
    )
    return choice
