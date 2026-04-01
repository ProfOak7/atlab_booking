import streamlit as st
import pandas as pd
from storage import get_connection

st.title("My Bookings")

canvas_user_id = st.text_input("Enter your Canvas User ID")

if canvas_user_id.strip():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                b.booking_id,
                b.canvas_user_id,
                b.status,
                b.created_at,
                s.start_time,
                s.end_time,
                s.location,
                e.exam_number,
                e.exam_name,
                t.term_name
            FROM bookings b
            JOIN slots s ON b.slot_id = s.slot_id
            JOIN exams e ON s.exam_id = e.exam_id
            JOIN terms t ON e.term_id = t.term_id
            WHERE b.canvas_user_id = ?
            ORDER BY s.start_time
        """, (canvas_user_id.strip(),)).fetchall()

    bookings = [dict(row) for row in rows]

    if bookings:
        df = pd.DataFrame(bookings)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bookings found for that Canvas User ID.")
