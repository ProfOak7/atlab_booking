import streamlit as st
import pandas as pd
from storage import get_terms, add_term, get_courses, add_course

st.title("Admin: Course Shells")

st.header("Add Term")

with st.form("add_term_form"):
    term_name = st.text_input("Term name", placeholder="Spring 2026")
    start_date = st.text_input("Start date", placeholder="2026-01-12")
    end_date = st.text_input("End date", placeholder="2026-05-22")
    active = st.checkbox("Set as active term")
    submitted_term = st.form_submit_button("Add term")

    if submitted_term:
        if term_name:
            add_term(term_name, start_date, end_date, int(active))
            st.success(f"Added term: {term_name}")
            st.rerun()
        else:
            st.error("Please enter a term name.")

st.divider()

terms = get_terms()

st.header("Add Course Shell")

if not terms:
    st.warning("Add a term first.")
else:
    term_options = {f"{t['term_name']} (ID {t['term_id']})": t["term_id"] for t in terms}

    with st.form("add_course_form"):
        selected_term_label = st.selectbox("Term", list(term_options.keys()))
        canvas_course_id = st.text_input("Canvas course ID")
        course_name = st.text_input("Course name", placeholder="BIO 205 Human Anatomy")
        section_name = st.text_input("Section name", placeholder="30371")
        notes = st.text_area("Notes")
        submitted_course = st.form_submit_button("Add course shell")

        if submitted_course:
            if canvas_course_id and course_name:
                add_course(
                    term_id=term_options[selected_term_label],
                    canvas_course_id=canvas_course_id,
                    course_name=course_name,
                    section_name=section_name,
                    notes=notes
                )
                st.success(f"Added course shell: {course_name}")
                st.rerun()
            else:
                st.error("Please enter at least Canvas course ID and course name.")

st.divider()

st.header("Current Course Registry")
courses = get_courses()

if courses:
    df = pd.DataFrame(courses)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No courses added yet.")
