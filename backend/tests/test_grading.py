"""
Quiz değerlendirme (grading) testleri — bellek içi SQLite ile, ağ yok.
"""
from __future__ import annotations

import json

import pytest

from app.models import QuizQuestion, QuizAttempt, UserProgress
from app.quiz.grading import grade_answer


def _add_question(db, correct_index: int = 1) -> QuizQuestion:
    q = QuizQuestion(
        topic="test-konu",
        question_text="Örnek soru?",
        options_json=json.dumps(["A", "B", "C", "D"]),
        correct_index=correct_index,
        explanation="Açıklama metni.",
        related_glossary_slug=None,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def test_correct_answer_updates_progress(db_session):
    """Doğru cevap: is_correct True, ilerleme 1/1."""
    q = _add_question(db_session, correct_index=2)
    result = grade_answer(db_session, q.id, selected_index=2)

    assert result["is_correct"] is True
    assert result["correct_index"] == 2
    assert result["explanation"] == "Açıklama metni."

    progress = db_session.query(UserProgress).filter_by(topic="test-konu").first()
    assert progress.total_count == 1
    assert progress.correct_count == 1


def test_wrong_answer_records_attempt(db_session):
    """Yanlış cevap: is_correct False, deneme kaydı düşer, doğru sayacı artmaz."""
    q = _add_question(db_session, correct_index=1)
    result = grade_answer(db_session, q.id, selected_index=3)

    assert result["is_correct"] is False

    attempts = db_session.query(QuizAttempt).all()
    assert len(attempts) == 1
    assert attempts[0].selected_index == 3
    assert attempts[0].is_correct is False

    progress = db_session.query(UserProgress).filter_by(topic="test-konu").first()
    assert progress.total_count == 1
    assert progress.correct_count == 0


def test_progress_accumulates_across_answers(db_session):
    """Birden çok cevap ilerlemeyi biriktirmeli (2 doğru, 1 yanlış → 2/3)."""
    q = _add_question(db_session, correct_index=0)
    grade_answer(db_session, q.id, selected_index=0)  # doğru
    grade_answer(db_session, q.id, selected_index=0)  # doğru
    grade_answer(db_session, q.id, selected_index=1)  # yanlış

    progress = db_session.query(UserProgress).filter_by(topic="test-konu").first()
    assert progress.total_count == 3
    assert progress.correct_count == 2


def test_missing_question_raises(db_session):
    """Var olmayan soru id'si ValueError fırlatmalı."""
    with pytest.raises(ValueError, match="Soru bulunamadı"):
        grade_answer(db_session, question_id=99999, selected_index=0)
