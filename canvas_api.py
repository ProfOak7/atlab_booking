import requests
import streamlit as st

BASE_URL = st.secrets["CANVAS_BASE_URL"]
API_TOKEN = st.secrets["CANVAS_API_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


def get_course_enrollments(course_id):
    """
    Get all enrollments for a course.
    """
    url = f"{BASE_URL}/api/v1/courses/{course_id}/enrollments"

    params = {
        "type[]": "StudentEnrollment",
        "per_page": 100
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return None

    return response.json()


def get_user_profile(user_id):
    """
    Get user profile by Canvas user ID.
    """
    url = f"{BASE_URL}/api/v1/users/{user_id}/profile"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return None

    return response.json()
