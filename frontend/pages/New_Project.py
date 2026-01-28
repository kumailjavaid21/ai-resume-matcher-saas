import streamlit as st
import requests

from frontend.utils import BACKEND_URL, api_headers

st.header("New Project")
if not st.session_state.get("token"):
    st.warning("Login first on the Login page.")
else:
    with st.form("project_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create Project")
        if submitted and title:
            response = requests.post(
                f"{BACKEND_URL}/projects",
                json={"title": title, "description": description},
                headers=api_headers(),
            )
            if response.ok:
                project = response.json()
                st.success(f"Project created (ID {project['id']}).")
                st.session_state["projects"] = None
                st.session_state["selected_project"] = project["id"]
            else:
                st.error(response.text)

    projects = st.session_state.get("projects") or []
    if projects:
        st.subheader("Your projects")
        st.table(
            [
                {
                    "ID": project["id"],
                    "Title": project["title"],
                    "Description": project.get("description") or "-",
                }
                for project in projects
            ]
        )
    else:
        st.info("Once you have created a project it will appear in the sidebar and here.")
