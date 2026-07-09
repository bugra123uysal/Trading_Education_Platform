import json

import streamlit as st

from app.database import session_scope
from app.i18n import get_lang, t
from app.models import QuizQuestion
from app.quiz.scenario import generate_scenario
from app.quiz.grading import grade_answer
from ui.common import indicator_figure, term_expander

TOPIC_IDS = ["temel-kavramlar", "teknik-analiz", "risk-yonetimi", "grafik-okuma"]


def render():
    st.title(t("quiz_title"))
    st.write(t("quiz_intro"))

    tab_labels = [t("quiz_tab_scenario")] + [t(f"topic_{tid}") for tid in TOPIC_IDS]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_scenario()

    for tab, topic_id in zip(tabs[1:], TOPIC_IDS):
        with tab:
            _render_topic_quiz(topic_id)


TARGETS = [110, 120, 150, 200, 300, 500]
START_BALANCE = 100.0


def _next_target(balance: float):
    for target in TARGETS:
        if balance < target:
            return target
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
    b1.metric(t("scen_balance"), f"${balance:,.2f}", t("scen_balance_delta", delta=balance - START_BALANCE))
    b2.metric(t("scen_next_target"), f"${target}" if target else t("scen_all_targets"))
    b3.metric(t("scen_trades"), st.session_state.game_trades)
    if target:
        prev = START_BALANCE if target == TARGETS[0] else TARGETS[TARGETS.index(target) - 1]
        pct = max(0.0, min(1.0, (balance - prev) / (target - prev)))
        st.progress(pct, text=t("scen_progress", target=target))
    if balance <= 10:
        st.error(t("scen_low_balance"))
        if st.button(t("scen_reset_btn"), key="reset_game"):
            st.session_state.game_balance = START_BALANCE
            st.session_state.game_trades = 0
            st.session_state.game_reached = []
            st.session_state.scenario = None
            st.session_state.scenario_choice = None
            st.rerun()

    st.divider()
    st.subheader(t("scen_date_header", symbol=scenario["symbol"], date=scenario["cut_date"]))
    st.write(t("scen_intro", symbol=scenario["symbol"], date=scenario["cut_date"], balance=balance))

    if st.session_state.scenario_choice is None:
        st.plotly_chart(
            indicator_figure(scenario["candles_before"]),
            use_container_width=True,
            key="scenario_chart_before",
        )
        c1, c2, c3 = st.columns(3)
        if c1.button(t("scen_buy_btn"), key="choice_al", use_container_width=True):
            st.session_state.scenario_choice = "al"
            _apply_trade(scenario, "al")
            st.rerun()
        if c2.button(t("scen_short_btn"), key="choice_sat", use_container_width=True):
            st.session_state.scenario_choice = "sat"
            _apply_trade(scenario, "sat")
            st.rerun()
        if c3.button(t("scen_wait_btn"), key="choice_bekle", use_container_width=True):
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
                vline_label=t("scen_trade_moment"),
            ),
            use_container_width=True,
            key="scenario_chart_after",
        )
        if choice != "bekle":
            point = t("scen_buy_point") if choice == "al" else t("scen_short_point")
            st.caption(t("scen_caption_traded", date=scenario["cut_date"], point=point))
        else:
            st.caption(t("scen_caption_wait", date=scenario["cut_date"]))

        outcome = scenario["outcome_pct"]
        went = t("scen_went_up") if outcome >= 0 else t("scen_went_down")
        good_call = (choice == "al" and outcome >= 0) or (choice == "sat" and outcome < 0)

        # Bakiye değişimi
        pnl = st.session_state.get("last_pnl", 0.0)
        message = t("scen_outcome", pct=abs(outcome), went=went)
        new_balance = st.session_state.game_balance
        if choice == "bekle":
            st.info(t("scen_wait_result", msg=message))
        elif good_call:
            st.success(t("scen_win_result", msg=message, pnl=pnl, balance=new_balance))
        else:
            st.error(t("scen_loss_result", msg=message, pnl=abs(pnl), balance=new_balance))

        # Yeni hedefe ulaşıldı mı?
        for target in TARGETS:
            if st.session_state.game_balance >= target and target not in st.session_state.game_reached:
                st.session_state.game_reached.append(target)
                st.balloons()
                st.success(t("scen_target_reached", target=target,
                             next=_next_target(st.session_state.game_balance) or "—"))

        # Eğitici geri bildirim — grafiği okumaya yardımcı
        _educational_feedback(scenario, choice, good_call)

        if scenario.get("reasoning"):
            st.markdown(t("scen_reasoning_header"))
            for note in scenario["reasoning"]:
                st.write(f"- {note}")
            st.caption(t("scen_reasoning_note"))

        term_expander("stop-loss", label_prefix=t("scen_risk_prefix"))

        if st.button(t("scen_new_btn"), key="new_scenario_btn"):
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


def _educational_feedback(scenario: dict, choice: str, good_call: bool) -> None:
    """İşleme ve teknik görünüme göre grafiği okumayı öğreten tavsiyeler (seçili dilde)."""
    st.markdown(t("scen_edu_header"))

    trend_up = scenario.get("trend_up", False)
    tips: list[str] = []

    if choice == "al":
        tips.append(t("scen_tip_buy_trend_up") if trend_up else t("scen_tip_buy_trend_down"))
    elif choice == "sat":
        tips.append(t("scen_tip_short_trend_up") if trend_up else t("scen_tip_short_trend_down"))
    else:
        tips.append(t("scen_tip_wait"))

    if choice != "bekle":
        tips.append(t("scen_tip_win") if good_call else t("scen_tip_loss"))

    tips.append(t("scen_tip_reading_order"))

    for tip in tips:
        st.write(f"- {tip}")


def _render_topic_quiz(topic_id: str):
    q_key = f"quiz_{topic_id}_questions"
    idx_key = f"quiz_{topic_id}_index"
    correct_key = f"quiz_{topic_id}_correct"
    result_key = f"quiz_{topic_id}_result"

    if q_key not in st.session_state:
        with session_scope() as db:
            questions = db.query(QuizQuestion).filter(QuizQuestion.topic == topic_id).all()
            # Her iki dili de sakla; gösterirken seçili dile göre seçilir
            # (dil değişse bile şık sırası aynı olduğu için index geçerli kalır).
            st.session_state[q_key] = [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_text_en": q.question_text_en,
                    "options": json.loads(q.options_json),
                    "options_en": json.loads(q.options_json_en) if q.options_json_en else None,
                }
                for q in questions
            ]
        st.session_state[idx_key] = 0
        st.session_state[correct_key] = 0
        st.session_state[result_key] = None

    questions = st.session_state[q_key]
    index = st.session_state[idx_key]
    en = get_lang() == "en"

    if not questions:
        st.info(t("quiz_no_questions"))
        return

    if index >= len(questions):
        st.subheader(t("quiz_done"))
        st.write(t("quiz_score", total=len(questions), correct=st.session_state[correct_key]))
        if st.button(t("quiz_restart"), key=f"restart_{topic_id}"):
            del st.session_state[q_key]
            st.rerun()
        return

    q = questions[index]
    q_text = q["question_text_en"] if en and q.get("question_text_en") else q["question_text"]
    options = q["options_en"] if en and q.get("options_en") else q["options"]

    st.caption(t("quiz_question_n", i=index + 1, total=len(questions)))
    st.subheader(q_text)

    result = st.session_state[result_key]

    if result is None:
        choice = st.radio(t("quiz_options"), options, key=f"radio_{topic_id}_{q['id']}", label_visibility="collapsed")
        if st.button(t("quiz_answer_btn"), key=f"answer_{topic_id}_{q['id']}"):
            selected_index = options.index(choice)
            with session_scope() as db:
                graded = grade_answer(db, q["id"], selected_index)
            if graded["is_correct"]:
                st.session_state[correct_key] += 1
            st.session_state[result_key] = graded
            st.rerun()
    else:
        if result["is_correct"]:
            st.success(t("quiz_correct"))
        else:
            st.error(t("quiz_wrong", answer=options[result["correct_index"]]))
        explanation = result.get("explanation_en") if en and result.get("explanation_en") else result["explanation"]
        st.write(explanation)
        if result["related_glossary_slug"]:
            term_expander(result["related_glossary_slug"])

        label = t("quiz_next") if index + 1 < len(questions) else t("quiz_finish")
        if st.button(label, key=f"next_{topic_id}"):
            st.session_state[idx_key] += 1
            st.session_state[result_key] = None
            st.rerun()
