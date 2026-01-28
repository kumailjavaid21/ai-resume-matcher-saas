import streamlit as st

from frontend.utils import login, signup

st.header("Login / Signup")
with st.form("auth_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_submitted = st.form_submit_button("Login")
    signup_submitted = st.form_submit_button("Signup")
    if login_submitted and email and password:
        payload = login(email, password)
        if payload:
            st.session_state["token"] = payload["access_token"]
            st.success("Logged in.")
    if signup_submitted and email and password:
        payload = signup(email, password)
        if payload:
            st.session_state["token"] = payload["access_token"]
            st.success("Account created and logged in.")
