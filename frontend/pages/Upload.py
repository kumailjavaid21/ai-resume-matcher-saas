import streamlit as st
import requests

from frontend.utils import BACKEND_URL, api_headers

st.header("Upload Job Description & Resumes")
if not st.session_state.get("token"):
    st.warning("Login before uploading files.")
else:
    project_id = st.session_state.get("selected_project")
    if project_id:
        st.info(f"Uploading documents for project ID: {project_id}")
    else:
        project_id_input = st.text_input("Project ID")
        project_id = project_id_input.strip()
    jd_file = st.file_uploader("Job Description (PDF)", type=["pdf"])
    resumes = st.file_uploader("Resumes (PDF, multiple allowed)", type=["pdf"], accept_multiple_files=True)

    if st.button("Upload JD"):
        if not project_id:
            st.warning("Select or enter a project ID first.")
        elif not jd_file:
            st.warning("Attach a JD PDF before uploading.")
        else:
            response = requests.post(
                f"{BACKEND_URL}/upload/jd?project_id={project_id}",
                files={"file": (jd_file.name, jd_file.getvalue(), "application/pdf")},
                headers=api_headers(),
            )
            if response.ok:
                st.success("JD uploaded.")
            else:
                st.error(response.text)

    if st.button("Upload Resumes"):
        if not project_id:
            st.warning("Select or enter a project ID first.")
        elif not resumes:
            st.warning("Attach resume PDFs before uploading.")
        else:
            files_payload = [("files", (resume.name, resume.getvalue(), "application/pdf")) for resume in resumes]
            response = requests.post(
                f"{BACKEND_URL}/upload/resumes?project_id={project_id}",
                files=files_payload,
                headers=api_headers(),
            )
            if response.ok:
                st.success("Resumes uploaded.")
            else:
                st.error(response.text)
