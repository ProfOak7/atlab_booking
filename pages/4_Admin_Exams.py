import streamlit as st
import pandas as pd
from storage import get_terms, get_exams, add_exam, seed_default_lab_exams

st.title("Admin: Exams")

terms = get_terms()

if not terms:
    st.warning("Please add a term first on the Course Shells page.")
    st.stop()

term_options = {f"{t['term_name']} (ID {t['term_id']})": t["term_id"] for t in terms}

st.header("Seed Default Lab Exams (2-10)")

with st.form("seed_exams_form"):
    selected_seed_term = st.selectbox("Select term to seed", list(term_options.keys()), key="seed_term")
    seed_submitted = st.form_submit_button("Seed Lab Exams 2-10")

    if seed_submitted:
        term_id = term_options[selected_seed_term]
        added_count = seed_default_lab_exams(term_id)
        if added_count > 0:
            st.success(f"Added {added_count} exams.")
        else:
            st.info("All default lab exams already exist for that term.")
        st.rerun()

st.divider()

st.header("Add Single Exam Manually")

with st.form("add_exam_form"):
    selected_term = st.selectbox("Term", list(term_options.keys()), key="manual_term")
    exam_number = st.number_input("Exam number", min_value=2, max_value=20, step=1, value=2)
    exam_name = st.text_input("Exam name", placeholder="Cytology, Histology, & the Integumentary System")
    active = st.checkbox("Active", value=True)
    submitted_exam = st.form_submit_button("Add exam")

    if submitted_exam:
        if exam_name.strip():
            add_exam(
                term_id=term_options[selected_term],
                exam_number=int(exam_number),
                exam_name=exam_name.strip(),
                active=int(active)
            )
            st.success(f"Added Lab Exam {int(exam_number)}.")
            st.rerun()
        else:
            st.error("Please enter an exam name.")

st.divider()

st.header("Current Exams")

exams = get_exams()

if exams:
    df = pd.DataFrame(exams)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No exams added yet.")
