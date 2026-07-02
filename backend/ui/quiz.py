import json

import streamlit as st

from app.database import session_scope
from app.models import QuizQuestion
from app.quiz.scenario import generate_scenario
from app.quiz.grading import grade_answer
from ui.common import indicator_figure, term_expander

TOPICS = [
    ("temel-kavramlar", "Temel Kavramlar"),
    ("teknik-analiz", "Teknik Analiz"),
    ("risk-yonetimi", "Risk Yönetimi"),
]


def render():
    st.title("Quiz")
    st.write("Bilgini test et ya da gerçek bir piyasa senaryosunda ne yapacağına karar ver.")

    tab_labels = ["Senaryo Sorusu"] + [label for _, label in TOPICS]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_scenario()

    for tab, (topic_id, topic_label) in zip(tabs[1:], TOPICS):
        with tab:
            _render_topic_quiz(topic_id, topic_label)


TARGETS = [110, 120, 150, 200, 300, 500]
START_BALANCE = 100.0


def _next_target(balance: float):
    for t in TARGETS:
        if balance < t:
            return t
    return None


def _render_scenario():
    if "scenario" not in st.session_state:
        st.session_state.scenario = None
        st.session_state.scenario_choice = None
    if "game_balance" not in st.session_state:
        st.session_state.game_balance = START_BALANCE
        st.session_state.game_trades = 0
        st.session_state.game_reached = []

    if st.session_state.scenario is None:
        with session_scope() as db:
            st.session_state.scenario = generate_scenario(db)
        st.session_state.scenario_choice = None

    scenario = st.session_state.scenario
    balance = st.session_state.game_balance

    # --- Oyun durumu: bakiye + hedef ---
    target = _next_target(balance)
    b1, b2, b3 = st.columns(3)
    b1.metric("Bakiyen", f"${balance:,.2f}", f"{balance - START_BALANCE:+,.2f}$ toplam")
    b2.metric("Sıradaki Hedef", f"${target}" if target else "Tüm hedefler tamam! 🏆")
    b3.metric("İşlem Sayısı", st.session_state.game_trades)
    if target:
        prev = START_BALANCE if target == TARGETS[0] else TARGETS[TARGETS.index(target) - 1]
        pct = max(0.0, min(1.0, (balance - prev) / (target - prev)))
        st.progress(pct, text=f"${target} hedefine ilerleme")
    if balance <= 10:
        st.error("Bakiyen çok azaldı! Gerçek hayatta bu noktaya gelmeden risk yönetimi devreye girmeliydi.")
        if st.button("Oyunu Sıfırla ($100 ile yeniden başla)", key="reset_game"):
            st.session_state.game_balance = START_BALANCE
            st.session_state.game_trades = 0
            st.session_state.game_reached = []
            st.session_state.scenario = None
            st.session_state.scenario_choice = None
            st.rerun()

    st.divider()
    st.subheader(f"{scenario['symbol']} — {scenario['cut_date']} tarihindesin")
    st.write(
        f"Aşağıdaki grafik, {scenario['symbol']} hissesinin {scenario['cut_date']} tarihine kadar olan "
        f"gerçek fiyat hareketini gösteriyor. Bakiyenin tamamıyla (${balance:,.2f}) işlem yapıyorsun: "
        "**Al** dersen yükselişten kazanırsın, **Sat (açığa satış)** dersen düşüşten kazanırsın, "
        "**Bekle** dersen bakiyen değişmez."
    )

    if st.session_state.scenario_choice is None:
        st.plotly_chart(
            indicator_figure(scenario["candles_before"]),
            use_container_width=True,
            key="scenario_chart_before",
        )
        c1, c2, c3 = st.columns(3)
        if c1.button("AL (yükseliş beklerim)", key="choice_al", use_container_width=True):
            st.session_state.scenario_choice = "al"
            _apply_trade(scenario, "al")
            st.rerun()
        if c2.button("SAT — açığa satış (düşüş beklerim)", key="choice_sat", use_container_width=True):
            st.session_state.scenario_choice = "sat"
            _apply_trade(scenario, "sat")
            st.rerun()
        if c3.button("BEKLE (işleme girmem)", key="choice_bekle", use_container_width=True):
            st.session_state.scenario_choice = "bekle"
            _apply_trade(scenario, "bekle")
            st.rerun()
    else:
        choice = st.session_state.scenario_choice
        all_candles = scenario["candles_before"] + scenario["candles_after"]

        # İşleme girdiğin noktayı grafikte işaretle
        markers = []
        if choice == "al":
            markers.append({"date": scenario["cut_date"], "color": "#3fb27f"})
        elif choice == "sat":
            markers.append({"date": scenario["cut_date"], "color": "#d9534f"})
        st.plotly_chart(
            indicator_figure(
                all_candles,
                markers=markers,
                vline_date=scenario["cut_date"],
                vline_label="İşlem anı",
            ),
            use_container_width=True,
            key="scenario_chart_after",
        )
        if choice != "bekle":
            st.caption(
                f"Sarı kesikli çizgi, {scenario['cut_date']} tarihinde işleme girdiğin anı gösteriyor — "
                "çizginin solu karar verirken gördüğün grafik, sağı işlemden sonra gerçekte yaşananlar. "
                f"{'Yeşil yukarı ok = ALIŞ noktası.' if choice == 'al' else 'Kırmızı aşağı ok = AÇIĞA SATIŞ noktası.'}"
            )
        else:
            st.caption(
                f"Sarı kesikli çizgi, {scenario['cut_date']} tarihindeki karar anını gösteriyor — "
                "çizginin solu karar verirken gördüğün grafik, sağı sonrasında gerçekte yaşananlar."
            )

        outcome = scenario["outcome_pct"]
        went = "yükseldi" if outcome >= 0 else "düştü"
        good_call = (choice == "al" and outcome >= 0) or (choice == "sat" and outcome < 0)

        # Bakiye değişimi
        pnl = st.session_state.get("last_pnl", 0.0)
        message = f"Sonraki 20 gün içinde fiyat %{abs(outcome)} {went}."
        if choice == "bekle":
            st.info(message + " Sen beklemeyi seçtin — bakiyen değişmedi.")
        elif good_call:
            st.success(f"{message} Doğru yöndeydin: **+${pnl:,.2f}** kazandın. Yeni bakiyen: ${st.session_state.game_balance:,.2f}")
        else:
            st.error(f"{message} Ters yöndeydin: **-${abs(pnl):,.2f}** kaybettin. Yeni bakiyen: ${st.session_state.game_balance:,.2f}")

        # Yeni hedefe ulaşıldı mı?
        for t in TARGETS:
            if st.session_state.game_balance >= t and t not in st.session_state.game_reached:
                st.session_state.game_reached.append(t)
                st.balloons()
                st.success(f"🎯 ${t} hedefine ulaştın! Sıradaki hedef: ${_next_target(st.session_state.game_balance) or '—'}")

        # Eğitici geri bildirim — grafiği okumaya yardımcı
        _educational_feedback(scenario, choice, good_call, outcome)

        if scenario.get("reasoning"):
            st.markdown("**Grafiğin bu yöne neden ilerlemiş olabileceğine dair teknik gözlemler:**")
            for note in scenario["reasoning"]:
                st.write(f"- {note}")
            st.caption(
                "Not: Bunlar fiyat/hacim verisinden çıkarılan teknik gözlemlerdir, kesin bir "
                "neden-sonuç kanıtı değildir. Karmaşık finans terimleri temiz bir anlatımla "
                "açıklanmıştır; gerçek hayatta fiyatı haberler, kazanç açıklamaları gibi "
                "teknik göstergede görünmeyen olaylar da etkiler."
            )

        term_expander("stop-loss", label_prefix="Riskini nasıl sınırlarsın")

        if st.button("Yeni Senaryo", key="new_scenario_btn"):
            st.session_state.scenario = None
            st.session_state.scenario_choice = None
            st.rerun()


def _apply_trade(scenario: dict, choice: str) -> None:
    """Seçime göre bakiyeyi günceller. AL: fiyatla aynı yönde, SAT (açığa satış): ters yönde kazanç."""
    outcome = scenario["outcome_pct"]
    balance = st.session_state.game_balance
    if choice == "al":
        pnl = balance * outcome / 100
    elif choice == "sat":
        pnl = balance * (-outcome) / 100
    else:
        pnl = 0.0
    st.session_state.game_balance = round(balance + pnl, 2)
    st.session_state.last_pnl = round(pnl, 2)
    if choice != "bekle":
        st.session_state.game_trades += 1


def _educational_feedback(scenario: dict, choice: str, good_call: bool, outcome: float) -> None:
    """İşleme ve teknik görünüme göre grafiği okumayı öğreten tavsiyeler."""
    st.markdown("### 📖 Bu işlemden ne öğrenebilirsin?")

    reasoning = scenario.get("reasoning", [])
    trend_up = any("üzerindeydi" in n and "200" in n for n in reasoning[:1])

    tips: list[str] = []

    if choice == "al":
        if trend_up:
            tips.append(
                "AL kararı verirken fiyatın 200 günlük EMA'nın üzerinde olması lehineydi — "
                "trend yönünde işlem yapmak ('trend dostundur' kuralı) genelde daha güvenlidir."
            )
        else:
            tips.append(
                "Fiyat 200 günlük EMA'nın altındayken AL demek 'düşen bıçağı tutmak' olarak "
                "adlandırılır — trende karşı işlem risklidir. Genelde fiyatın önce uzun vadeli "
                "ortalamanın üzerine çıkmasını beklemek daha güvenlidir."
            )
    elif choice == "sat":
        if trend_up:
            tips.append(
                "Yükseliş trendinde açığa satış yapmak en riskli işlemlerden biridir — güçlü "
                "trendler beklenenden çok daha uzun sürebilir. Açığa satışta zarar teorik "
                "olarak sınırsızdır, unutma."
            )
        else:
            tips.append(
                "Düşüş trendinde SAT demek trend yönünde bir karardı — açığa satışta bile "
                "trend yönünde işlem yapmak mantıklıdır. Yine de açığa satış her zaman "
                "yüksek risklidir."
            )
    else:
        tips.append(
            "Beklemek de bir pozisyondur. Profesyoneller net sinyal yoksa işleme girmez — "
            "'işlem yapmama disiplini' en az alım-satım kadar önemlidir."
        )

    if good_call and choice != "bekle":
        tips.append(
            "Kazandın ama dikkat: tek bir doğru tahmin, stratejinin işe yaradığını kanıtlamaz. "
            "Gerçek başarı, 50-100 işlemin toplamında kârda kalabilmektir."
        )
    elif not good_call and choice != "bekle":
        tips.append(
            "Kaybettin — ama bu kötü bir karar verdiğin anlamına gelmeyebilir. Doğru analizle "
            "girilen işlemler de kaybedebilir. Önemli olan: her işlemde bakiyenin en fazla "
            "%1-2'sini riske atmak. Bu oyunda tüm bakiyenle işlem yapıyorsun — gerçek hayatta bunu asla yapma!"
        )

    tips.append(
        "Grafiği okurken sıralama şöyle olmalı: önce trend (fiyat EMA 200'ün neresinde?), "
        "sonra momentum (EMA 50, EMA 200'ün üstünde mi?), sonra hacim (harekete katılım var mı?). "
        "Aşağıdaki teknik gözlemler bu sırayla yazıldı."
    )

    for tip in tips:
        st.write(f"- {tip}")


def _render_topic_quiz(topic_id: str, topic_label: str):
    q_key = f"quiz_{topic_id}_questions"
    idx_key = f"quiz_{topic_id}_index"
    correct_key = f"quiz_{topic_id}_correct"
    result_key = f"quiz_{topic_id}_result"

    if q_key not in st.session_state:
        with session_scope() as db:
            questions = db.query(QuizQuestion).filter(QuizQuestion.topic == topic_id).all()
            st.session_state[q_key] = [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "options": json.loads(q.options_json),
                }
                for q in questions
            ]
        st.session_state[idx_key] = 0
        st.session_state[correct_key] = 0
        st.session_state[result_key] = None

    questions = st.session_state[q_key]
    index = st.session_state[idx_key]

    if not questions:
        st.info("Bu konuda henüz soru yok.")
        return

    if index >= len(questions):
        st.subheader("Tamamlandı")
        st.write(f"{len(questions)} sorudan {st.session_state[correct_key]} tanesini doğru bildin.")
        if st.button("Tekrar Başla", key=f"restart_{topic_id}"):
            del st.session_state[q_key]
            st.rerun()
        return

    q = questions[index]
    st.caption(f"Soru {index + 1} / {len(questions)}")
    st.subheader(q["question_text"])

    result = st.session_state[result_key]

    if result is None:
        choice = st.radio("Seçenekler", q["options"], key=f"radio_{topic_id}_{q['id']}", label_visibility="collapsed")
        if st.button("Cevapla", key=f"answer_{topic_id}_{q['id']}"):
            selected_index = q["options"].index(choice)
            with session_scope() as db:
                graded = grade_answer(db, q["id"], selected_index)
            if graded["is_correct"]:
                st.session_state[correct_key] += 1
            st.session_state[result_key] = graded
            st.rerun()
    else:
        if result["is_correct"]:
            st.success("Doğru!")
        else:
            st.error(f"Yanlış. Doğru cevap: {q['options'][result['correct_index']]}")
        st.write(result["explanation"])
        if result["related_glossary_slug"]:
            term_expander(result["related_glossary_slug"])

        label = "Sonraki Soru" if index + 1 < len(questions) else "Bitir"
        if st.button(label, key=f"next_{topic_id}"):
            st.session_state[idx_key] += 1
            st.session_state[result_key] = None
            st.rerun()
