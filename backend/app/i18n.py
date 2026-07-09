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
    # --- Senaryo (oyunlaştırılmış) ---
    "scen_balance": {"tr": "Bakiyen", "en": "Your Balance"},
    "scen_balance_delta": {"tr": "{delta:+,.2f}$ toplam", "en": "{delta:+,.2f}$ total"},
    "scen_next_target": {"tr": "Sıradaki Hedef", "en": "Next Target"},
    "scen_all_targets": {"tr": "Tüm hedefler tamam! 🏆", "en": "All targets reached! 🏆"},
    "scen_trades": {"tr": "İşlem Sayısı", "en": "Trades"},
    "scen_progress": {"tr": "${target} hedefine ilerleme", "en": "Progress to ${target}"},
    "scen_low_balance": {
        "tr": "Bakiyen çok azaldı! Gerçek hayatta bu noktaya gelmeden risk yönetimi devreye girmeliydi.",
        "en": "Your balance is very low! In real life risk management should have kicked in before this point.",
    },
    "scen_reset_btn": {
        "tr": "Oyunu Sıfırla ($100 ile yeniden başla)",
        "en": "Reset Game (start over with $100)",
    },
    "scen_date_header": {"tr": "{symbol} — {date} tarihindesin", "en": "{symbol} — you're on {date}"},
    "scen_intro": {
        "tr": "Aşağıdaki grafik, {symbol} hissesinin {date} tarihine kadar olan gerçek fiyat "
              "hareketini gösteriyor. Bakiyenin tamamıyla (${balance:,.2f}) işlem yapıyorsun: "
              "**Al** dersen yükselişten kazanırsın, **Sat (açığa satış)** dersen düşüşten "
              "kazanırsın, **Bekle** dersen bakiyen değişmez.",
        "en": "The chart below shows {symbol}'s real price action up to {date}. You trade with "
              "your full balance (${balance:,.2f}): choose **Buy** to profit from a rise, "
              "**Sell (short)** to profit from a fall, or **Wait** to leave your balance unchanged.",
    },
    "scen_buy_btn": {"tr": "AL (yükseliş beklerim)", "en": "BUY (I expect a rise)"},
    "scen_short_btn": {"tr": "SAT — açığa satış (düşüş beklerim)", "en": "SELL — short (I expect a fall)"},
    "scen_wait_btn": {"tr": "BEKLE (işleme girmem)", "en": "WAIT (I stay out)"},
    "scen_trade_moment": {"tr": "İşlem anı", "en": "Trade moment"},
    "scen_caption_traded": {
        "tr": "Sarı kesikli çizgi, {date} tarihinde işleme girdiğin anı gösteriyor — çizginin "
              "solu karar verirken gördüğün grafik, sağı işlemden sonra gerçekte yaşananlar. {point}",
        "en": "The yellow dashed line marks the moment you entered on {date} — left of the line "
              "is the chart you saw when deciding, right of it is what actually happened. {point}",
    },
    "scen_caption_wait": {
        "tr": "Sarı kesikli çizgi, {date} tarihindeki karar anını gösteriyor — çizginin solu "
              "karar verirken gördüğün grafik, sağı sonrasında gerçekte yaşananlar.",
        "en": "The yellow dashed line marks the decision moment on {date} — left of the line is "
              "the chart you saw, right of it is what actually happened next.",
    },
    "scen_buy_point": {"tr": "Yeşil yukarı ok = ALIŞ noktası.", "en": "Green up-arrow = BUY point."},
    "scen_short_point": {"tr": "Kırmızı aşağı ok = AÇIĞA SATIŞ noktası.", "en": "Red down-arrow = SHORT point."},
    "scen_went_up": {"tr": "yükseldi", "en": "rose"},
    "scen_went_down": {"tr": "düştü", "en": "fell"},
    "scen_outcome": {
        "tr": "Sonraki 20 gün içinde fiyat %{pct} {went}.",
        "en": "Over the next 20 days the price {went} {pct}%.",
    },
    "scen_wait_result": {
        "tr": "{msg} Sen beklemeyi seçtin — bakiyen değişmedi.",
        "en": "{msg} You chose to wait — your balance didn't change.",
    },
    "scen_win_result": {
        "tr": "{msg} Doğru yöndeydin: **+${pnl:,.2f}** kazandın. Yeni bakiyen: ${balance:,.2f}",
        "en": "{msg} You were on the right side: you gained **+${pnl:,.2f}**. New balance: ${balance:,.2f}",
    },
    "scen_loss_result": {
        "tr": "{msg} Ters yöndeydin: **-${pnl:,.2f}** kaybettin. Yeni bakiyen: ${balance:,.2f}",
        "en": "{msg} You were on the wrong side: you lost **-${pnl:,.2f}**. New balance: ${balance:,.2f}",
    },
    "scen_target_reached": {
        "tr": "🎯 ${target} hedefine ulaştın! Sıradaki hedef: ${next}",
        "en": "🎯 You reached the ${target} target! Next target: ${next}",
    },
    "scen_new_btn": {"tr": "Yeni Senaryo", "en": "New Scenario"},
    "scen_risk_prefix": {"tr": "Riskini nasıl sınırlarsın", "en": "How to limit your risk"},
    # Eğitici geri bildirim
    "scen_edu_header": {"tr": "### 📖 Bu işlemden ne öğrenebilirsin?", "en": "### 📖 What can you learn from this trade?"},
    "scen_tip_buy_trend_up": {
        "tr": "AL kararı verirken fiyatın 200 günlük EMA'nın üzerinde olması lehineydi — "
              "trend yönünde işlem yapmak ('trend dostundur' kuralı) genelde daha güvenlidir.",
        "en": "Price being above the 200-day EMA was in your favor for the BUY — trading with "
              "the trend ('the trend is your friend') is usually safer.",
    },
    "scen_tip_buy_trend_down": {
        "tr": "Fiyat 200 günlük EMA'nın altındayken AL demek 'düşen bıçağı tutmak' olarak "
              "adlandırılır — trende karşı işlem risklidir. Genelde fiyatın önce uzun vadeli "
              "ortalamanın üzerine çıkmasını beklemek daha güvenlidir.",
        "en": "Buying while price is below the 200-day EMA is called 'catching a falling knife' "
              "— trading against the trend is risky. It's usually safer to wait for price to "
              "reclaim the long-term average first.",
    },
    "scen_tip_short_trend_up": {
        "tr": "Yükseliş trendinde açığa satış yapmak en riskli işlemlerden biridir — güçlü "
              "trendler beklenenden çok daha uzun sürebilir. Açığa satışta zarar teorik olarak "
              "sınırsızdır, unutma.",
        "en": "Shorting in an uptrend is one of the riskiest trades — strong trends can last far "
              "longer than expected. Remember, in short selling the loss is theoretically unlimited.",
    },
    "scen_tip_short_trend_down": {
        "tr": "Düşüş trendinde SAT demek trend yönünde bir karardı — açığa satışta bile trend "
              "yönünde işlem yapmak mantıklıdır. Yine de açığa satış her zaman yüksek risklidir.",
        "en": "Shorting in a downtrend was a with-the-trend decision — even in short selling, "
              "trading with the trend makes sense. Still, short selling is always high-risk.",
    },
    "scen_tip_wait": {
        "tr": "Beklemek de bir pozisyondur. Profesyoneller net sinyal yoksa işleme girmez — "
              "'işlem yapmama disiplini' en az alım-satım kadar önemlidir.",
        "en": "Waiting is a position too. Professionals stay out without a clear signal — the "
              "'discipline of not trading' matters as much as trading itself.",
    },
    "scen_tip_win": {
        "tr": "Kazandın ama dikkat: tek bir doğru tahmin, stratejinin işe yaradığını kanıtlamaz. "
              "Gerçek başarı, 50-100 işlemin toplamında kârda kalabilmektir.",
        "en": "You won, but note: one correct guess doesn't prove a strategy works. Real success "
              "is staying profitable across the sum of 50–100 trades.",
    },
    "scen_tip_loss": {
        "tr": "Kaybettin — ama bu kötü bir karar verdiğin anlamına gelmeyebilir. Doğru analizle "
              "girilen işlemler de kaybedebilir. Önemli olan: her işlemde bakiyenin en fazla "
              "%1-2'sini riske atmak. Bu oyunda tüm bakiyenle işlem yapıyorsun — gerçek hayatta bunu asla yapma!",
        "en": "You lost — but that may not mean you decided badly. Well-analyzed trades can lose "
              "too. What matters: risk at most 1–2% of your balance per trade. In this game you "
              "trade your whole balance — never do that in real life!",
    },
    "scen_tip_reading_order": {
        "tr": "Grafiği okurken sıralama şöyle olmalı: önce trend (fiyat EMA 200'ün neresinde?), "
              "sonra momentum (EMA 50, EMA 200'ün üstünde mi?), sonra hacim (harekete katılım var mı?). "
              "Aşağıdaki teknik gözlemler bu sırayla yazıldı.",
        "en": "Read a chart in this order: first trend (where is price relative to EMA 200?), then "
              "momentum (is EMA 50 above EMA 200?), then volume (is there participation?). The "
              "technical observations below are written in that order.",
    },
    "scen_reasoning_header": {
        "tr": "**Grafiğin bu yöne neden ilerlemiş olabileceğine dair teknik gözlemler:**",
        "en": "**Technical observations on why the chart may have moved this way:**",
    },
    "scen_reasoning_note": {
        "tr": "Not: Bunlar fiyat/hacim verisinden çıkarılan teknik gözlemlerdir, kesin bir "
              "neden-sonuç kanıtı değildir. Karmaşık finans terimleri temiz bir anlatımla "
              "açıklanmıştır; gerçek hayatta fiyatı haberler, kazanç açıklamaları gibi "
              "teknik göstergede görünmeyen olaylar da etkiler.",
        "en": "Note: these are technical observations drawn from price/volume data, not proof of "
              "cause and effect. In real life, price is also driven by news and earnings that "
              "don't appear on technical indicators.",
    },
    # --- Senaryo teknik gözlemleri (reasoning) ---
    "reason_above_200": {
        "tr": "Kesme noktasında fiyat, uzun vadeli eğilimi gösteren 200 günlük EMA'nın "
              "üzerindeydi — bu genellikle büyük resimde bir yükseliş trendine işaret eder.",
        "en": "At the cut point price was above the 200-day EMA (the long-term trend gauge) — "
              "this usually points to an uptrend in the big picture.",
    },
    "reason_below_200": {
        "tr": "Kesme noktasında fiyat, 200 günlük EMA'nın altındaydı — bu genellikle "
              "büyük resimde bir düşüş ya da zayıf trende işaret eder.",
        "en": "At the cut point price was below the 200-day EMA — this usually points to a "
              "downtrend or a weak trend in the big picture.",
    },
    "reason_ema50_above": {
        "tr": "Kısa vadeli ortalama (EMA 50), uzun vadeli ortalamanın (EMA 200) üzerindeydi — "
              "momentum yukarı yönlüydü.",
        "en": "The short-term average (EMA 50) was above the long-term average (EMA 200) — "
              "momentum was to the upside.",
    },
    "reason_ema50_below": {
        "tr": "Kısa vadeli ortalama (EMA 50), uzun vadeli ortalamanın (EMA 200) altındaydı — "
              "momentum aşağı yönlüydü.",
        "en": "The short-term average (EMA 50) was below the long-term average (EMA 200) — "
              "momentum was to the downside.",
    },
    "reason_dv_high": {
        "tr": "Son günlerde dolar hacmi, 50 günlük ortalamasının belirgin şekilde "
              "üzerindeydi — hisseye yoğun bir ilgi vardı.",
        "en": "In recent days dollar volume was clearly above its 50-day average — there was "
              "strong interest in the stock.",
    },
    "reason_dv_low": {
        "tr": "Son günlerde dolar hacmi, 50 günlük ortalamasının altındaydı — "
              "hisseye olan ilgi nispeten sönükleşmişti.",
        "en": "In recent days dollar volume was below its 50-day average — interest in the "
              "stock had relatively faded.",
    },
    "reason_dv_normal": {
        "tr": "Dolar hacmi son günlerde normal seviyelerdeydi, belirgin bir anormallik yoktu.",
        "en": "Dollar volume was at normal levels recently, with no clear anomaly.",
    },
    "reason_after_up_highvol": {
        "tr": "Sonrasında gerçekleşen yükseliş, ortalamanın üzerinde bir hacimle "
              "desteklendi — teknik analizde bu genelde hareketin 'sağlıklı' / "
              "katılımlı kabul edildiği bir işarettir.",
        "en": "The rise that followed was backed by above-average volume — in technical "
              "analysis this is usually seen as a 'healthy', participated move.",
    },
    "reason_after_down_highvol": {
        "tr": "Sonrasında gerçekleşen düşüş, ortalamanın üzerinde bir hacimle "
              "gerçekleşti — bu genelde satış baskısının güçlü olduğunu gösterir.",
        "en": "The decline that followed happened on above-average volume — this usually "
              "indicates strong selling pressure.",
    },
    "reason_after_lowvol": {
        "tr": "Sonraki hareket, düşük hacimle gerçekleşti — bu tür hareketler "
              "genelde daha az güvenilir kabul edilir, kolayca tersine dönebilir.",
        "en": "The subsequent move happened on low volume — such moves are usually considered "
              "less reliable and can reverse easily.",
    },
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
