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
