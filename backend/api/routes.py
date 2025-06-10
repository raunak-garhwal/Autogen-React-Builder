from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from ..services.orchestrator import ProjectOrchestrator
from ..services.zip_creator import create_project_zip

router = APIRouter()

class ProjectConfig(BaseModel):
    project_name: str
    description: Optional[str] = ""
    features: List[str] = []
    state_management: bool = False
    routing: bool = False
    icons: bool = False
    animations: bool = False

@router.post("/generate")
async def generate_project(config: ProjectConfig, background_tasks: BackgroundTasks):
    try:
        print(f"\n[API] Received project generation request")
        print(f"[API] Project config: {config.dict()}")
        
        orchestrator = ProjectOrchestrator()
        project_id = await orchestrator.initialize_project(config)
        
        print(f"[API] Project initialized with ID: {project_id}")
        print(f"[API] Current project statuses: {orchestrator.project_status.keys()}")
        
        # Start project generation in background
        background_tasks.add_task(orchestrator.generate_project, project_id)
        
        return {
            "status": "success",
            "message": "Project generation started",
            "project_id": project_id
        }
    except Exception as e:
        print(f"[API] Error in generate_project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{project_id}")
async def get_project_status(project_id: str):
    try:
        print(f"\n[API] Checking status for project: {project_id}")
        orchestrator = ProjectOrchestrator()
        
        # Check if project exists in orchestrator's status tracking
        if project_id not in orchestrator.project_status:
            print(f"[API] Project {project_id} not found in status tracking")
            raise HTTPException(
                status_code=404,
                detail=f"Project {project_id} not found in status tracking"
            )
            
        status = await orchestrator.get_project_status(project_id)
        print(f"[API] Current status for {project_id}: {status}")
        return status
    except Exception as e:
        print(f"[API] Error in get_project_status: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{project_id}")
async def download_project(project_id: str):
    try:
        print(f"\n[API] Download requested for project: {project_id}")
        zip_path = f"generated/{project_id}.zip"
        if not os.path.exists(zip_path):
            print(f"[API] Project zip not found at: {zip_path}")
            raise HTTPException(status_code=404, detail="Project not found")
            
        print(f"[API] Sending project zip: {zip_path}")
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"{project_id}.zip"
        )
    except Exception as e:
        print(f"[API] Error in download_project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 