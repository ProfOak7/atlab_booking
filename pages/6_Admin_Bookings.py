import streamlit as st
import pandas as pd

from canvas_api import find_student_across_courses
from storage import get_courses

st.title("Admin: Bookings")

st.divider()
st.header("Test Student Lookup")

search = st.text_input("Enter student email or name")

if st.button("Find Student"):
    if not search.strip():
        st.error("Please enter a search value.")
    else:
        courses = get_courses()

        if not courses:
            st.warning("No course shells found. Add them first.")
            st.stop()

        course_ids = [c["canvas_course_id"] for c in courses]

        results = find_student_across_courses(search.strip(), course_ids)

        if results:
            st.success(f"Found {len(results)} match(es)")

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # Optional: show raw JSON for debugging
            with st.expander("Raw data"):
                st.json(results)

        else:
            st.warning("No student found.")
