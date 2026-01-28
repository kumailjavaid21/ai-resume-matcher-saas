import streamlit as st

from frontend.utils import BACKEND_URL, api_headers, fetch_projects

st.set_page_config(page_title="AI Resume Matcher", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None
if "projects" not in st.session_state:
    st.session_state["projects"] = None
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = None


def refresh_projects():
    if not st.session_state.get("token"):
        return
    response = fetch_projects()
    if response.ok:
        projects = response.json()
        st.session_state["projects"] = projects
        if projects:
            current_ids = {p["id"] for p in projects}
            if st.session_state["selected_project"] not in current_ids:
                st.session_state["selected_project"] = projects[0]["id"]
            # reset selectbox key to ensure updated options
            st.session_state.setdefault("project_selectbox", None)
        else:
            st.session_state["selected_project"] = None
    else:
        st.error("Unable to load projects: " + response.text)


def get_project_display_label(project_id: int) -> str:
    projects = st.session_state.get("projects") or []
    for project in projects:
        if project["id"] == project_id:
            return f'{project_id} — {project["title"]}'
    return str(project_id)


st.title("AI Resume Matcher Console")
st.write("Connect to the FastAPI backend at", BACKEND_URL)
st.sidebar.markdown("Use the pages in this app to manage authentication, projects, uploads, matching, and reports.")

if st.sidebar.button("Clear session"):
    st.session_state["token"] = None
    st.session_state["projects"] = None
    st.session_state["selected_project"] = None

if st.session_state.get("token"):
    if st.session_state["projects"] is None:
        refresh_projects()
    projects = st.session_state.get("projects") or []
    st.sidebar.subheader("Active project")
    if projects:
        options = [project["id"] for project in projects]
        try:
            index = options.index(st.session_state["selected_project"]) if st.session_state["selected_project"] in options else 0
        except ValueError:
            index = 0
        selected_id = st.sidebar.selectbox(
            "Select project",
            options,
            index=index,
            format_func=lambda pid: get_project_display_label(pid),
            key="project_selector",
        )
        st.session_state["selected_project"] = selected_id
        st.sidebar.markdown(f"**Selected:** {get_project_display_label(selected_id)}")
    else:
        st.sidebar.info("Create a project to start uploading documents.")
    if st.sidebar.button("Refresh projects"):
        refresh_projects()
