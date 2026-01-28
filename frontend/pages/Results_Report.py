import streamlit as st
import requests

from frontend.utils import BACKEND_URL, api_headers

st.header("Results & Report Download")
if not st.session_state.get("token"):
    st.warning("Login first.")
else:
    project_id = st.session_state.get("selected_project")
    if project_id:
        st.info(f"Viewing results for project ID {project_id}")
    else:
        project_id_input = st.text_input("Project ID")
        project_id = project_id_input.strip()
    if st.button("Fetch Results"):
        if not project_id:
            st.warning("Select or enter a project ID first.")
        else:
            response = requests.get(f"{BACKEND_URL}/match/results?project_id={project_id}", headers=api_headers())
            if response.ok:
                data = response.json()
                st.subheader("Job Description")
                st.write(data["jd"])
                st.subheader("Matches")
                for match in data["matches"]:
                    st.markdown(f"**Resume {match['resume_id']}** – score {match['score']}")
                    st.write("Matched skills:", match["matched_skills"])
                    st.write("Missing required:", match["missing_required"])
                    st.write("Missing preferred:", match["missing_preferred"])
                    st.write("Suggestions:", match["improvement_suggestions"])
            else:
                st.error(response.text)
    if project_id:
        st.markdown(f"[Download latest report]({BACKEND_URL}/reports/{project_id}.pdf)")
