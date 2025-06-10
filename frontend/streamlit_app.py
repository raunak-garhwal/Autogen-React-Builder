import streamlit as st
import requests
import json
import time
from typing import Dict, Optional

# Configure page
st.set_page_config(
    page_title="AutoGen React Builder",
    page_icon="⚛️",
    layout="wide"
)

# Constants
API_URL = "http://localhost:8000/api"

def init_session_state():
    """Initialize session state variables."""
    if "project_id" not in st.session_state:
        st.session_state.project_id = None
    if "generation_complete" not in st.session_state:
        st.session_state.generation_complete = False
    if "current_status" not in st.session_state:
        st.session_state.current_status = None

def create_project(config: Dict) -> Optional[str]:
    """Create a new project."""
    try:
        print(f"[DEBUG] Creating project with config: {config}")
        response = requests.post("http://localhost:8000/api/generate", json=config)
        print(f"[DEBUG] Create project response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            project_id = data.get("project_id")
            print(f"[DEBUG] Created project with ID: {project_id}")
            return project_id
        else:
            print(f"[DEBUG] Error creating project: {response.status_code} - {response.text}")
            st.error(f"Error creating project: {response.text}")
            return None
    except Exception as e:
        print(f"[DEBUG] Exception in create_project: {str(e)}")
        st.error(f"Error creating project: {str(e)}")
        return None

def get_project_status(project_id: str) -> dict:
    """Get the current status of project generation."""
    try:
        print(f"[DEBUG] Requesting status for project ID: {project_id}")
        response = requests.get(f"http://localhost:8000/api/status/{project_id}")
        print(f"[DEBUG] Status response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[DEBUG] Error getting status: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[DEBUG] Exception in get_project_status: {str(e)}")
        return None

def download_project(project_id: str):
    """Download the generated project."""
    try:
        response = requests.get(f"{API_URL}/download/{project_id}")
        response.raise_for_status()
        
        # Create download button
        st.download_button(
            label="Download Project",
            data=response.content,
            file_name=f"{project_id}.zip",
            mime="application/zip"
        )
        return True
    except Exception as e:
        st.error(f"Error downloading project: {str(e)}")
        return False

def render_header():
    """Render the application header."""
    st.title("⚛️ AutoGen React Builder")
    st.markdown("""
    Create modern React applications with AI-powered code generation.
    Configure your project settings below and let AutoGen handle the rest!
    """)

def render_config_form():
    """Render the project configuration form."""
    print("[DEBUG] Starting render_config_form")
    with st.form("project_config"):
        # Basic Information
        st.subheader("Project Information")
        project_name = st.text_input("Project Name", placeholder="my-react-app")
        description = st.text_area("Description", placeholder="A modern React application")
        
        # Styling
        st.subheader("Styling")
        styling = st.selectbox(
            "Styling Solution",
            options=["tailwind", "css-modules", "styled-components"],
            index=0
        )
        
        # Features
        st.subheader("Features")
        col1, col2 = st.columns(2)
        
        with col1:
            state_management = st.selectbox(
                "State Management",
                options=["None", "zustand", "redux-toolkit"],
                index=0
            )
            
            routing = st.checkbox("Add React Router", value=True)
            
        with col2:
            ui_framework = st.selectbox(
                "UI Framework",
                options=["None", "shadcn", "material-ui"],
                index=0
            )
            
            animations = st.checkbox("Add Framer Motion", value=False)
            
        # Development Tools
        st.subheader("Development Tools")
        dev_tools = st.checkbox("Add Development Tools", value=False,
            help="Includes Monaco Editor, testing setup, and debugging utilities")
            
        # Submit Button
        submitted = st.form_submit_button("Generate Project")
        
        if submitted:
            print(f"[DEBUG] Form submitted with project name: {project_name}")
            if not project_name:
                st.error("Please enter a project name")
                return
                
            config = {
                "project_name": project_name,
                "description": description,
                "styling": styling,
                "state_management": state_management if state_management != "None" else None,
                "routing": routing,
                "ui_framework": ui_framework if ui_framework != "None" else None,
                "animations": animations,
                "dev_tools": dev_tools
            }
            print(f"[DEBUG] Generated config: {config}")
            
            with st.spinner("Initializing project generation..."):
                project_id = create_project(config)
                if project_id:
                    print(f"[DEBUG] Project initialized with ID: {project_id}")
                    st.session_state.project_id = project_id
                    st.session_state.generation_complete = False
            st.rerun()

def render_progress():
    """Render the generation progress."""
    print("[DEBUG] Starting render_progress")
    if not st.session_state.project_id:
        return
        
    st.subheader("Generation Progress")
    
    # Create progress placeholder
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    while not st.session_state.generation_complete:
        status = get_project_status(st.session_state.project_id)
        print(f"[DEBUG] Current status: {status}")
        
        if not status:
            time.sleep(1)
            continue
            
        st.session_state.current_status = status
        
        # Update progress
        progress = status.get("progress", 0)
        progress_placeholder.progress(progress / 100)
        
        # Update status message
        current_phase = status.get("current_phase", "")
        status_message = f"Current Phase: {current_phase.title()}"
        
        if status.get("errors"):
            print("[DEBUG] Errors found in status")
            status_message += "\n\n⚠️ Errors:"
            for error in status["errors"]:
                status_message += f"\n- {error['message']}"
                
        status_placeholder.markdown(status_message)
            
        # Check if complete
        if status.get("status") == "completed":
            print("[DEBUG] Project generation completed")
            st.session_state.generation_complete = True
            st.rerun()
        elif status.get("status") == "error":
            print("[DEBUG] Project generation failed")
            st.error("Project generation failed")
            break
            
        time.sleep(1)

def render_download():
    """Render the download section."""
    print("[DEBUG] Starting render_download")
    if not st.session_state.generation_complete:
        return
        
    st.subheader("Download Project")
    st.success("🎉 Project generation completed successfully!")
    
    # Show project summary
    if st.session_state.current_status:
        st.markdown("### Project Summary")
        st.json(st.session_state.current_status.get("config", {}))
        
        # Add download button
        if download_project(st.session_state.project_id):
            print("[DEBUG] Project downloaded successfully")
    
    # Add restart button
    if st.button("Generate Another Project"):
        print("[DEBUG] Starting new project")
        st.session_state.project_id = None
        st.session_state.generation_complete = False
        st.session_state.current_status = None
        st.rerun()

def main():
    """Main application entry point."""
    print("[DEBUG] Starting main application")
    init_session_state()
    render_header()
    
    if not st.session_state.project_id:
        render_config_form()
    elif not st.session_state.generation_complete:
        render_progress()
    else:
        render_download()

if __name__ == "__main__":
    main() 