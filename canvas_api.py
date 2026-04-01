import requests
import streamlit as st

BASE_URL = st.secrets["CANVAS_BASE_URL"]
API_TOKEN = st.secrets["CANVAS_API_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


def get_all_enrollments(course_id):
    url = f"{BASE_URL}/api/v1/courses/{course_id}/enrollments"

    params = {
        "type[]": "StudentEnrollment",
        "per_page": 100
    }

    all_results = []

    while url:
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            return None

        data = response.json()
        all_results.extend(data)

        # Handle pagination
        if "next" in response.links:
            url = response.links["next"]["url"]
            params = {}  # important: don't reuse params after first call
        else:
            url = None

    return all_results


def find_student_across_courses(search_value, course_ids):
    """
    search_value = Cuesta username, email, or name
    course_ids = list of Canvas course IDs
    """
    matches = []
    search_value = search_value.strip().lower()

    for course_id in course_ids:
        enrollments = get_all_enrollments(course_id)

        if not enrollments:
            continue

        for e in enrollments:
            user = e.get("user", {})  

            login_id = user.get("login_id", "").lower()
            name = user.get("name", "").lower()

            # Extract username from email
            username = login_id.split("@")[0] if "@" in login_id else login_id

            if (
                search_value == username or
                search_value in login_id or
                search_value in name
            ):
                matches.append({
                    "canvas_user_id": user.get("id"),
                    "name": user.get("name"),
                    "email": login_id,
                    "course_id": course_id,
                    "section_id": e.get("course_section_id")
                })

    return matches
