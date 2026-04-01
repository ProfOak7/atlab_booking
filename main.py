import streamlit as st
from storage import init_db

st.set_page_config(
    page_title="AT Lab Booking App",
    layout="wide"
)

init_db()

# -----------------------------
# Admin auth helpers
# -----------------------------
def check_admin_password():
    """Simple admin password gate for prototype use."""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    def handle_login():
        entered = st.session_state.get("admin_password_input", "")
        expected = st.secrets.get("ADMIN_PASSWORD", "")
        if entered and entered == expected:
            st.session_state.admin_authenticated = True
            st.session_state.admin_password_input = ""
        else:
            st.session_state.admin_authenticated = False
            st.session_state.admin_login_error = True

    def handle_logout():
        st.session_state.admin_authenticated = False

    with st.sidebar:
        st.markdown("### Admin Access")

        if st.session_state.admin_authenticated:
            st.success("Admin unlocked")
            st.button("Log out", on_click=handle_logout, use_container_width=True)
        else:
            st.text_input(
                "Enter admin password",
                type="password",
                key="admin_password_input",
            )
            st.button("Unlock Admin", on_click=handle_login, use_container_width=True)

            if st.session_state.get("admin_login_error", False):
                st.error("Incorrect password")
                st.session_state.admin_login_error = False

    return st.session_state.admin_authenticated


# -----------------------------
# Sidebar branding
# -----------------------------
st.sidebar.title("AT Lab Navigation")
st.sidebar.caption("Cuesta College AT Lab Oral Exam Booking")

is_admin = check_admin_password()

# -----------------------------
# Define pages
# -----------------------------
student_pages = [
    st.Page("pages/1_Student_Booking.py", title="Book Appointment", icon="🗓️"),
    st.Page("pages/2_My_Bookings.py", title="My Bookings", icon="📋"),
]

admin_pages = []
if is_admin:
    admin_pages = [
        st.Page("pages/3_Admin_Course_Shells.py", title="Admin: Course Shells", icon="🏫"),
        st.Page("pages/4_Admin_Exams.py", title="Admin: Exams", icon="🧪"),
        st.Page("pages/5_Admin_Slots.py", title="Admin: Slots", icon="⏰"),
        st.Page("pages/6_Admin_Bookings.py", title="Admin: Bookings", icon="📚"),
    ]

nav_sections = {"Student": student_pages}
if admin_pages:
    nav_sections["Admin"] = admin_pages

pg = st.navigation(nav_sections)
pg.run()
