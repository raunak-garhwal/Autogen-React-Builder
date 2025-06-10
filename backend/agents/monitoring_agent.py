from autogen import AssistantAgent, UserProxyAgent
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class MonitoringAgent:
    def __init__(self, config_list):
        try:
            self.config_list = config_list
            self.assistant = AssistantAgent(
                name="monitoring_expert",
                system_message="""You are an expert in monitoring and error handling.
                Your role is to track project generation progress, handle errors gracefully,
                and provide detailed status updates.""",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.7
                }
            )
            
            # Ensure the generated directory exists
            os.makedirs("generated", exist_ok=True)
            
            # Initialize the user proxy with Docker disabled
            self.user_proxy = UserProxyAgent(
                name="monitoring_manager",
                code_execution_config={
                    "work_dir": "generated",
                    "use_docker": False
                },
                human_input_mode="NEVER"
            )
            
            self.status_cache = {}
        except Exception as e:
            print(f"Error initializing MonitoringAgent: {str(e)}")
            raise

    async def initialize_monitoring(self, project_id: str) -> bool:
        """Initialize monitoring for a new project."""
        try:
            # Create project directory
            project_dir = os.path.join("generated", project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Initialize status
            status = {
                "project_id": project_id,
                "start_time": datetime.now().isoformat(),
                "status": "initializing",
                "current_phase": None,
                "completed_tasks": [],
                "pending_tasks": [],
                "errors": [],
                "warnings": [],
                "progress": 0,
                "config": {}  # Will be populated later
            }
            
            self.status_cache[project_id] = status
            success = await self._save_status(project_id, status)
            
            if not success:
                raise Exception("Failed to save initial status")
                
            return True
        except Exception as e:
            print(f"Error initializing monitoring: {str(e)}")
            return False

    async def update_status(
        self,
        project_id: str,
        status: Optional[str] = None,
        current_phase: Optional[str] = None,
        completed_task: Optional[str] = None,
        error: Optional[str] = None,
        warning: Optional[str] = None
    ) -> bool:
        """Update the project status."""
        try:
            current_status = await self.get_status(project_id)
            
            if not current_status:
                raise Exception(f"No status found for project {project_id}")
                
            if status:
                current_status["status"] = status
                
            if current_phase:
                current_status["current_phase"] = current_phase
                
            if completed_task:
                if completed_task not in current_status["completed_tasks"]:
                    current_status["completed_tasks"].append(completed_task)
                if completed_task in current_status["pending_tasks"]:
                    current_status["pending_tasks"].remove(completed_task)
                    
            if error:
                error_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "message": error,
                    "phase": current_phase or current_status.get("current_phase", "unknown")
                }
                current_status["errors"].append(error_entry)
                await self._log_error(project_id, error_entry)
                
            if warning:
                current_status["warnings"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": warning
                })
                
            # Update progress
            total_tasks = len(current_status["completed_tasks"]) + len(current_status["pending_tasks"])
            if total_tasks > 0:
                current_status["progress"] = (len(current_status["completed_tasks"]) / total_tasks) * 100
                
            self.status_cache[project_id] = current_status
            return await self._save_status(project_id, current_status)
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            return False

    async def get_status(self, project_id: str) -> Dict:
        """Get the current status of a project."""
        try:
            # Try to get from cache first
            status = self.status_cache.get(project_id)
            
            # If not in cache, try to load from file
            if not status:
                status = await self._load_status(project_id)
                if status:
                    self.status_cache[project_id] = status
                    
            return status or {}
        except Exception as e:
            print(f"Error getting status: {str(e)}")
            return {}

    async def add_pending_tasks(self, project_id: str, tasks: List[str]) -> bool:
        """Add pending tasks to be tracked."""
        try:
            current_status = await self.get_status(project_id)
            
            if not current_status:
                raise Exception(f"No status found for project {project_id}")
                
            for task in tasks:
                if task not in current_status["pending_tasks"] and task not in current_status["completed_tasks"]:
                    current_status["pending_tasks"].append(task)
                    
            return await self._save_status(project_id, current_status)
        except Exception as e:
            print(f"Error adding pending tasks: {str(e)}")
            return False

    async def handle_error(self, project_id: str, error: str, phase: str) -> bool:
        """Handle an error that occurred during project generation."""
        try:
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "phase": phase,
                "error": error
            }
            
            # Update status with error
            await self.update_status(
                project_id=project_id,
                status="error",
                current_phase=phase,
                error=error
            )
            
            # Log error
            await self._log_error(project_id, error_entry)
            return True
        except Exception as e:
            print(f"Error handling error: {str(e)}")
            return False

    async def _save_status(self, project_id: str, status: Dict) -> bool:
        """Save status to file."""
        try:
            status_dir = os.path.join("generated", project_id)
            os.makedirs(status_dir, exist_ok=True)
            
            status_file = os.path.join(status_dir, "status.json")
            with open(status_file, "w") as f:
                json.dump(status, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving status: {str(e)}")
            return False

    async def _load_status(self, project_id: str) -> Optional[Dict]:
        """Load status from file."""
        try:
            status_file = os.path.join("generated", project_id, "status.json")
            
            if not os.path.exists(status_file):
                return None
                
            with open(status_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading status: {str(e)}")
            return None

    async def _log_error(self, project_id: str, error_entry: Dict) -> bool:
        """Log an error to the project's error log file."""
        try:
            log_dir = os.path.join("generated", project_id, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "error.log")
            with open(log_file, "a") as f:
                f.write(json.dumps(error_entry) + "\n")
                
            return True
        except Exception as e:
            print(f"Error logging error: {str(e)}")
            return False 