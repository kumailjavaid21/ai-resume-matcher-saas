import streamlit as st
import requests

from frontend.utils import BACKEND_URL, api_headers

st.header("Run Matching")
if not st.session_state.get("token"):
    st.warning("Login first.")
else:
    project_id = st.session_state.get("selected_project")
    if project_id:
        st.info(f"Running matching for project ID {project_id}")
    else:
        project_id_input = st.text_input("Project ID")
        project_id = project_id_input.strip()
    if st.button("Run Matching Pipeline"):
        if not project_id:
            st.warning("Select or enter a project ID before running matching.")
        else:
            response = requests.post(f"{BACKEND_URL}/match/run?project_id={project_id}", headers=api_headers())
            if response.ok:
                data = response.json()
                st.success(f"Run completed. Best score: {data.get('best_score')}")
                st.json(data)
            else:
                st.error(response.text)
