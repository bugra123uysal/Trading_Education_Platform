"""
Quiz cevap değerlendirme mantığı. UI katmanından ayrı tutuyoruz ki
"bir cevap doğru mu, ilerleme nasıl güncellenir" kuralı tek bir yerde
yaşasın.
"""
from sqlalchemy.orm import Session

from app.models import QuizQuestion, QuizAttempt, UserProgress


def grade_answer(db: Session, question_id: int, selected_index: int) -> dict:
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if question is None:
        raise ValueError("Soru bulunamadı.")

    is_correct = selected_index == question.correct_index

    db.add(QuizAttempt(question_id=question.id, selected_index=selected_index, is_correct=is_correct))

    progress = db.query(UserProgress).filter(UserProgress.topic == question.topic).first()
    if progress is None:
        progress = UserProgress(topic=question.topic, correct_count=0, total_count=0)
        db.add(progress)
    progress.total_count += 1
    if is_correct:
        progress.correct_count += 1

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_index": question.correct_index,
        "explanation": question.explanation,
        "explanation_en": question.explanation_en,
        "related_glossary_slug": question.related_glossary_slug,
    }
