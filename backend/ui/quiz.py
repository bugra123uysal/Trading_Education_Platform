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


def _render_scenario():
    if "scenario" not in st.session_state:
        st.session_state.scenario = None
        st.session_state.scenario_choice = None

    if st.session_state.scenario is None:
        with session_scope() as db:
            st.session_state.scenario = generate_scenario(db)
        st.session_state.scenario_choice = None

    scenario = st.session_state.scenario

    st.subheader(f"{scenario['symbol']} — {scenario['cut_date']} tarihindesin")
    st.write(
        f"Aşağıdaki grafik, {scenario['symbol']} hissesinin {scenario['cut_date']} tarihine kadar olan "
        "gerçek fiyat hareketini gösteriyor. Bu noktada elinde bu hisseden olsaydın, ne yapardın?"
    )

    if st.session_state.scenario_choice is None:
        st.plotly_chart(
            indicator_figure(scenario["candles_before"]),
            use_container_width=True,
            key="scenario_chart_before",
        )
        c1, c2, c3 = st.columns(3)
        if c1.button("Alırdım / Tutardım", key="choice_al", use_container_width=True):
            st.session_state.scenario_choice = "al"
            st.rerun()
        if c2.button("Satardım", key="choice_sat", use_container_width=True):
            st.session_state.scenario_choice = "sat"
            st.rerun()
        if c3.button("Beklerdim", key="choice_bekle", use_container_width=True):
            st.session_state.scenario_choice = "bekle"
            st.rerun()
    else:
        choice = st.session_state.scenario_choice
        all_candles = scenario["candles_before"] + scenario["candles_after"]
        st.plotly_chart(indicator_figure(all_candles), use_container_width=True, key="scenario_chart_after")

        outcome = scenario["outcome_pct"]
        went = "yükseldi" if outcome >= 0 else "düştü"
        good_call = (choice == "al" and outcome >= 0) or (choice == "sat" and outcome < 0)

        message = f"Sonraki 20 gün içinde fiyat %{abs(outcome)} {went}."
        if outcome >= 0:
            st.success(message)
        else:
            st.error(message)

        if choice == "bekle":
            st.write(
                "Beklemeyi seçtin — bazen hiçbir şey yapmamak da bir karardır, "
                "özellikle ne yapacağından emin değilsen."
            )
        elif good_call:
            st.write(
                "Bu sefer tahminin gerçekleşen yönle uyumluydu. Ama unutma: bu tek bir örnek, "
                "piyasayı tutarlı şekilde öngörmek çok zordur."
            )
        else:
            st.write(
                "Bu sefer fiyat beklediğinin tersi yöne gitti. Bu çok normal — kısa vadeli fiyat "
                "hareketlerini öngörmek profesyoneller için bile zordur. Önemli olan riski önceden sınırlamaktır."
            )

        if scenario.get("reasoning"):
            st.markdown("**Grafiğin bu yöne neden ilerlemiş olabileceğine dair teknik gözlemler:**")
            for note in scenario["reasoning"]:
                st.write(f"- {note}")
            st.caption(
                "Not: Bunlar fiyat/hacim verisinden çıkarılan teknik gözlemlerdir, kesin bir "
                "neden-sonuç kanıtı değildir. Gerçek hayatta fiyatı haberler, kazanç açıklamaları "
                "gibi teknik göstergede görünmeyen olaylar da etkiler."
            )

        term_expander("stop-loss", label_prefix="Riskini nasıl sınırlarsın")

        if st.button("Yeni Senaryo", key="new_scenario_btn"):
            st.session_state.scenario = None
            st.session_state.scenario_choice = None
            st.rerun()


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
