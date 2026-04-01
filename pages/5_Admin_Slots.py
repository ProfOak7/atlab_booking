import streamlit as st
import pandas as pd
from storage import (
    get_terms,
    get_exam_options,
    get_availability_templates,
    add_availability_template,
    delete_availability_template,
    seed_default_availability,
    generate_slots_from_templates,
    get_slots,
)

st.title("Admin: Slots")

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

terms = get_terms()
if not terms:
    st.warning("Please add a term first.")
    st.stop()

term_options = {f"{t['term_name']} (ID {t['term_id']})": t["term_id"] for t in terms}

st.header("1. Availability Templates")

selected_term_label = st.selectbox("Select term", list(term_options.keys()))
selected_term_id = term_options[selected_term_label]

col1, col2 = st.columns(2)

with col1:
    if st.button("Seed Default Availability"):
        added = seed_default_availability(selected_term_id)
        if added > 0:
            st.success(f"Added {added} default availability rows.")
        else:
            st.info("Default availability already exists.")
        st.rerun()

with col2:
    st.caption("Default = SLO Mon-Fri 9-5 + Sat 9-1, NCC Mon-Fri 9-5")

with st.form("add_availability_form"):
    location = st.selectbox("Location", ["SLO", "NCC"])
    day_of_week = st.selectbox(
        "Day of week",
        options=list(DAY_NAMES.keys()),
        format_func=lambda x: DAY_NAMES[x]
    )
    start_time = st.text_input("Start time", value="09:00")
    end_time = st.text_input("End time", value="17:00")
    submitted = st.form_submit_button("Add availability row")

    if submitted:
        add_availability_template(
            term_id=selected_term_id,
            location=location,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
        st.success("Availability row added.")
        st.rerun()

templates = get_availability_templates(selected_term_id)

if templates:
    st.subheader("Current availability")
    template_df = pd.DataFrame(templates)
    if "day_of_week" in template_df.columns:
        template_df["day_name"] = template_df["day_of_week"].map(DAY_NAMES)
    st.dataframe(template_df, use_container_width=True)

    st.subheader("Delete availability row")
    delete_options = {
        f"{t['location']} | {DAY_NAMES[t['day_of_week']]} | {t['start_time']}-{t['end_time']} | Template ID {t['template_id']}": t["template_id"]
        for t in templates
    }
    selected_delete = st.selectbox("Select row to delete", list(delete_options.keys()))
    if st.button("Delete selected availability row"):
        delete_availability_template(delete_options[selected_delete])
        st.success("Availability row deleted.")
        st.rerun()
else:
    st.info("No availability rows yet for this term.")

st.divider()

st.header("2. Generate Slots for an Exam")

exam_options_raw = [
    exam for exam in get_exam_options()
    if selected_term_id == next((t["term_id"] for t in terms if t["term_id"] == selected_term_id), selected_term_id)
]

# Better filtering by term name display already selected
all_exams = get_exam_options()
selected_term_name = next(t["term_name"] for t in terms if t["term_id"] == selected_term_id)
exam_options = {
    f"Lab Exam {e['exam_number']} - {e['exam_name']} ({e['term_name']})": e["exam_id"]
    for e in all_exams
    if e["term_name"] == selected_term_name
}

if not exam_options:
    st.warning("No active exams found for this term. Add exams first.")
    st.stop()

with st.form("generate_slots_form"):
    selected_exam_label = st.selectbox("Select exam", list(exam_options.keys()))
    date_start = st.date_input("Start date")
    date_end = st.date_input("End date")
    slot_minutes = st.number_input("Slot length (minutes)", min_value=15, max_value=240, value=60, step=15)
    capacity = st.number_input("Capacity per slot", min_value=1, max_value=10, value=1, step=1)

    submitted_generate = st.form_submit_button("Generate slots")

    if submitted_generate:
        if date_end < date_start:
            st.error("End date must be on or after start date.")
        else:
            added = generate_slots_from_templates(
                exam_id=exam_options[selected_exam_label],
                term_id=selected_term_id,
                date_start=str(date_start),
                date_end=str(date_end),
                slot_minutes=int(slot_minutes),
                capacity=int(capacity),
            )
            st.success(f"Added {added} slots.")
            st.rerun()

st.divider()

st.header("3. Current Slots")

slots = get_slots()
slots_for_term = [s for s in slots if s["term_name"] == selected_term_name]

if slots_for_term:
    slots_df = pd.DataFrame(slots_for_term)
    st.dataframe(slots_df, use_container_width=True)
else:
    st.info("No slots generated yet for this term.")
