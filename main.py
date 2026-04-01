import streamlit as st
from storage import init_db

st.set_page_config(page_title="AT Lab Booking App", layout="wide")

init_db()

st.title("AT Lab Booking App")
st.write("Welcome! The database has been initialized.")
st.info("Use the sidebar to navigate once pages are added.")
