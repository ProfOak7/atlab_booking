import streamlit as st
from storage import init_db

st.set_page_config(
    page_title="AT Lab Booking App",
    layout="wide"
)

init_db()

# ---- Shared sidebar ----
st.sidebar.title("AT Lab Navigation")
st.sidebar.caption("Cuesta College AT Lab Oral Exam Booking")

# ---- Define pages ----
student_pages = [
    st.Page("pages/1_Student_Booking.py", title="Book Appointment", icon="🗓️"),
    st.Page("pages/2_My_Bookings.py", title="My Bookings", icon="📋"),
]

admin_pages = [
    st.Page("pages/3_Admin_Course_Shells.py", title="Admin: Course Shells", icon="🏫"),
    st.Page("pages/4_Admin_Exams.py", title="Admin: Exams", icon="🧪"),
    st.Page("pages/5_Admin_Slots.py", title="Admin: Slots", icon="⏰"),
]

pg = st.navigation(
    {
        "Student": student_pages,
        "Admin": admin_pages,
    }
)

pg.run()
