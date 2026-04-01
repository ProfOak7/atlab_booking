import streamlit as st
from canvas_api import get_course_enrollments

st.title("Admin: Bookings")

course_id = st.text_input("Test Canvas Course ID")

if st.button("Fetch Students"):
    data = get_course_enrollments(course_id)

    if data:
        st.write(f"Found {len(data)} students")
        st.json(data[:3])
    else:
        st.error("Failed to fetch enrollments")
