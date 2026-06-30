import streamlit as st

from app.database import session_scope
from app.models import GlossaryTerm
from ui.common import CATEGORY_LABELS


def render():
    st.title("Terim Sözlüğü")
    st.write("Trading'de sık karşılaşacağın terimleri burada çocuğa anlatır gibi, sade bir dille açıklıyoruz.")

    search = st.text_input("Terim Ara", placeholder="örn: stop-loss, RSI, hacim...")

    with session_scope() as db:
        terms = db.query(GlossaryTerm).order_by(GlossaryTerm.term.asc()).all()
        terms = [
            {
                "slug": t.slug,
                "term": t.term,
                "category": t.category,
                "short_definition": t.short_definition,
                "child_explanation": t.child_explanation,
                "example": t.example,
            }
            for t in terms
        ]

    if search.strip():
        s = search.strip().lower()
        terms = [t for t in terms if s in t["term"].lower() or s in t["short_definition"].lower()]

    if not terms:
        st.info("Aramanızla eşleşen bir terim bulunamadı.")
        return

    for t in terms:
        with st.expander(f"{t['term']}  —  {t['short_definition']}"):
            st.caption(CATEGORY_LABELS.get(t["category"], t["category"]))
            st.write(t["child_explanation"])
            if t["example"]:
                st.info(t["example"])
