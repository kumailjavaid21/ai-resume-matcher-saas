import os

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def api_headers():
    token = st.session_state.get("token")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def login(email: str, password: str) -> dict | None:
    response = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password})
    if response.ok:
        return response.json()
    st.error("Login failed: " + response.text)
    return None


def signup(email: str, password: str) -> dict | None:
    response = requests.post(f"{BACKEND_URL}/auth/signup", json={"email": email, "password": password})
    if response.ok:
        return response.json()
    st.error("Signup failed: " + response.text)
    return None


def fetch_projects():
    return requests.get(f"{BACKEND_URL}/projects", headers=api_headers())
