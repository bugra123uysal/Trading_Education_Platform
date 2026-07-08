import streamlit as st

from app.database import session_scope
from app.i18n import t
from app.models import GlossaryTerm
from ui.common import category_label, loc


def render():
    st.title(t("glossary_title"))
    st.write(t("glossary_intro"))

    search = st.text_input(t("glossary_search"), placeholder=t("glossary_search_ph"))

    with session_scope() as db:
        rows = db.query(GlossaryTerm).all()
        terms = [
            {
                "term": loc(r, "term"),
                "category": r.category,
                "short_definition": loc(r, "short_definition"),
                "child_explanation": loc(r, "child_explanation"),
                "example": loc(r, "example"),
            }
            for r in rows
        ]

    terms.sort(key=lambda x: x["term"].lower())

    if search.strip():
        s = search.strip().lower()
        terms = [t_ for t_ in terms if s in t_["term"].lower() or s in t_["short_definition"].lower()]

    if not terms:
        st.info(t("glossary_no_match"))
        return

    for item in terms:
        with st.expander(f"{item['term']}  —  {item['short_definition']}"):
            st.caption(category_label(item["category"]))
            st.write(item["child_explanation"])
            if item["example"]:
                st.info(item["example"])
