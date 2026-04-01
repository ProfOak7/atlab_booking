import streamlit as st
import pandas as pd
from datetime import datetime

from canvas_api import find_student_across_courses
from storage import (
    get_courses,
    get_active_terms,
    get_exams_by_term,
    get_available_slots_for_exam,
    get_slot_by_id,
    student_has_booking_same_exam_same_week,
    create_booking,
)

st.title("Student Booking")

st.write("Book your AT Lab oral exam appointment.")

# -----------------------------
# STEP 1: Identify student
# -----------------------------
st.header("Step 1: Find Yourself")

search = st.text_input("Enter your Cuesta username (same as your email without the @my.cuesta.edu).")

student_selected = None

if st.button("Find Me"):
    if not search.strip():
        st.error("Please enter your cuesta username")
    else:
        courses = get_courses()
        course_ids = [c["canvas_course_id"] for c in courses]

        results = find_student_across_courses(search.strip(), course_ids)

        if not results:
            st.error("No matching student found. Please check your email.")
        else:
            st.session_state["student_matches"] = results

# -----------------------------
# STEP 2: Select correct match
# -----------------------------
if "student_matches" in st.session_state:
    matches = st.session_state["student_matches"]

    st.header("Step 2: Confirm Your Identity")

    options = {
        f"{m['name']} ({m['email']}) - Course {m['course_id']}": m
        for m in matches
    }

    selected_label = st.selectbox("Select your record", list(options.keys()))
    student_selected = options[selected_label]

    st.success(f"Selected: {student_selected['name']}")

# -----------------------------
# STEP 3: Choose exam
# -----------------------------
if student_selected:
    st.header("Step 3: Select Exam")

    terms = get_active_terms()
    term_options = {t["term_name"]: t["term_id"] for t in terms}

    selected_term_name = st.selectbox("Select term", list(term_options.keys()))
    selected_term_id = term_options[selected_term_name]

    exams = get_exams_by_term(selected_term_id)

    if not exams:
        st.warning("No exams available.")
        st.stop()

    exam_options = {
        f"Lab Exam {e['exam_number']} - {e['exam_name']}": e["exam_id"]
        for e in exams
    }

    selected_exam_label = st.selectbox("Select exam", list(exam_options.keys()))
    selected_exam_id = exam_options[selected_exam_label]

    # -----------------------------
    # STEP 4: Choose slot
    # -----------------------------
    st.header("Step 4: Select Appointment Time")

    slots = get_available_slots_for_exam(selected_exam_id)

    if not slots:
        st.info("No available slots.")
        st.stop()

    def format_slot(slot):
        start_dt = datetime.strptime(slot["start_time"], "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(slot["end_time"], "%Y-%m-%d %H:%M")
        return f"{start_dt.strftime('%a %m/%d %I:%M %p')} - {end_dt.strftime('%I:%M %p')} | {slot['location']}"

    slot_options = {
        format_slot(s): s["slot_id"]
        for s in slots
    }

    selected_slot_label = st.selectbox("Available times", list(slot_options.keys()))
    selected_slot_id = slot_options[selected_slot_label]

    # -----------------------------
    # STEP 5: Book
    # -----------------------------
    st.header("Step 5: Confirm Booking")

    if st.button("Book Appointment"):
        slot = get_slot_by_id(selected_slot_id)

        already_booked = student_has_booking_same_exam_same_week(
            canvas_user_id=str(student_selected["canvas_user_id"]),
            exam_id=slot["exam_id"],
            slot_start_time=slot["start_time"],
        )

        if already_booked:
            st.error("You already have an appointment for this exam during the same week.")
        else:
            create_booking(
                slot_id=selected_slot_id,
                canvas_user_id=str(student_selected["canvas_user_id"]),
                canvas_course_id=str(student_selected["course_id"]),
                section_id=str(student_selected["section_id"]),
            )

            st.success("🎉 Appointment booked successfully!")
            st.balloons()
