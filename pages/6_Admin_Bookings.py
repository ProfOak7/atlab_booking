import streamlit as st
import pandas as pd

from storage import (
    get_all_bookings,
    cancel_booking,
)

st.title("Admin: Bookings")

bookings = get_all_bookings()

if not bookings:
    st.info("No bookings found yet.")
    st.stop()

df = pd.DataFrame(bookings)

st.header("Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    term_options = ["All"] + sorted(df["term_name"].dropna().unique().tolist())
    selected_term = st.selectbox("Term", term_options)

with col2:
    exam_options = ["All"] + sorted(
        [f"Lab Exam {n}" for n in df["exam_number"].dropna().unique().tolist()],
        key=lambda x: int(x.replace("Lab Exam ", ""))
    )
    selected_exam = st.selectbox("Exam", exam_options)

with col3:
    location_options = ["All"] + sorted(df["location"].dropna().unique().tolist())
    selected_location = st.selectbox("Location", location_options)

with col4:
    status_options = ["All"] + sorted(df["status"].dropna().unique().tolist())
    selected_status = st.selectbox("Status", status_options)

student_search = st.text_input(
    "Search by Canvas User ID or Course ID",
    placeholder="e.g. 12345"
)

filtered_df = df.copy()

if selected_term != "All":
    filtered_df = filtered_df[filtered_df["term_name"] == selected_term]

if selected_exam != "All":
    exam_number = int(selected_exam.replace("Lab Exam ", ""))
    filtered_df = filtered_df[filtered_df["exam_number"] == exam_number]

if selected_location != "All":
    filtered_df = filtered_df[filtered_df["location"] == selected_location]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]

if student_search.strip():
    search_value = student_search.strip().lower()
    filtered_df = filtered_df[
        filtered_df["canvas_user_id"].astype(str).str.lower().str.contains(search_value) |
        filtered_df["canvas_course_id"].astype(str).str.lower().str.contains(search_value)
    ]

st.divider()
st.header("Current Bookings")

if filtered_df.empty:
    st.warning("No bookings match the selected filters.")
else:
    display_df = filtered_df.copy()
    st.dataframe(display_df, use_container_width=True)

st.divider()
st.header("Cancel a Booking")

active_bookings = filtered_df[filtered_df["status"] == "booked"].copy()

if active_bookings.empty:
    st.info("No active bookings available to cancel in the current filter view.")
else:
    cancel_options = {
        (
            f"Booking {row['booking_id']} | "
            f"Lab Exam {row['exam_number']} | "
            f"{row['start_time']} | "
            f"{row['location']} | "
            f"Canvas User {row['canvas_user_id']}"
        ): int(row["booking_id"])
        for _, row in active_bookings.iterrows()
    }

    selected_cancel_label = st.selectbox(
        "Select booking to cancel",
        list(cancel_options.keys())
    )

    if st.button("Cancel Selected Booking"):
        booking_id = cancel_options[selected_cancel_label]
        cancel_booking(booking_id)
        st.success(f"Booking {booking_id} cancelled.")
        st.rerun()
