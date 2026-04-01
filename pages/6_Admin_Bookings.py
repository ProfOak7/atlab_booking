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
