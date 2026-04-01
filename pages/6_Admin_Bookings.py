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

from canvas_api import find_student_across_courses
from storage import get_courses

st.divider()
st.header("Test Student Lookup")

search = st.text_input("Enter student email or name")

if st.button("Find Student"):
    courses = get_courses()
    course_ids = [c["canvas_course_id"] for c in courses]

    results = find_student_across_courses(search, course_ids)

    if results:
        st.write(results)
    else:
        st.warning("No student found.")
