import streamlit as st
import pandas as pd
from datetime import datetime

from storage import (
    get_active_terms,
    get_exams_by_term,
    get_available_slots_for_exam,
    get_slot_by_id,
    student_has_booking_same_exam_same_week,
    create_booking,
)

st.title("Student Booking")

st.write("Use this page to book your AT Lab oral exam appointment.")

terms = get_active_terms()
if not terms:
    st.warning("No active terms available yet. Please contact your instructor.")
    st.stop()

term_options = {t["term_name"]: t["term_id"] for t in terms}
selected_term_name = st.selectbox("Select term", list(term_options.keys()))
selected_term_id = term_options[selected_term_name]

exams = get_exams_by_term(selected_term_id)
if not exams:
    st.warning("No active exams available for this term yet.")
    st.stop()

exam_options = {
    f"Lab Exam {e['exam_number']} - {e['exam_name']}": e["exam_id"]
    for e in exams
}
selected_exam_label = st.selectbox("Select exam", list(exam_options.keys()))
selected_exam_id = exam_options[selected_exam_label]

st.divider()

canvas_user_id = st.text_input(
    "Enter your Canvas User ID",
    help="Temporary for prototype testing. Later this can be replaced with Canvas lookup."
)

slots = get_available_slots_for_exam(selected_exam_id)

if not slots:
    st.info("No available slots for this exam yet.")
    st.stop()

slot_df = pd.DataFrame(slots)

def format_slot_label(slot):
    start_dt = datetime.strptime(slot["start_time"], "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(slot["end_time"], "%Y-%m-%d %H:%M")
    return f"{start_dt.strftime('%a %m/%d %I:%M %p')} - {end_dt.strftime('%I:%M %p')} | {slot['location']}"

slot_options = {
    format_slot_label(slot): slot["slot_id"]
    for slot in slots
}

selected_slot_label = st.selectbox("Available appointment times", list(slot_options.keys()))
selected_slot_id = slot_options[selected_slot_label]

st.divider()

if st.button("Book Appointment"):
    if not canvas_user_id.strip():
        st.error("Please enter your Canvas User ID.")
    else:
        slot = get_slot_by_id(selected_slot_id)

        if slot is None:
            st.error("Selected slot could not be found.")
        else:
            already_booked = student_has_booking_same_exam_same_week(
                canvas_user_id=canvas_user_id.strip(),
                exam_id=slot["exam_id"],
                slot_start_time=slot["start_time"],
            )

            if already_booked:
                st.error("You already have an appointment for this exam during the same week.")
            else:
                create_booking(
                    slot_id=selected_slot_id,
                    canvas_user_id=canvas_user_id.strip(),
                    canvas_course_id="",
                    section_id=""
                )
                st.success("Your appointment has been booked successfully!")
                st.rerun()
