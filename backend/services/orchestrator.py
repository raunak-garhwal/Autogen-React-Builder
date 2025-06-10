from typing import Dict, List, Optional
import os
import uuid
from datetime import datetime
from ..agents.planner_agent import PlannerAgent
from ..agents.foundation_agent import FoundationAgent
from ..agents.interface_agent import InterfaceAgent
from ..agents.state_motion_agent import StateMotionAgent
from ..services.zip_creator import create_project_zip
import json

class ProjectOrchestrator:
    # Class-level dictionary to store project status across instances
    _project_status = {}

    def __init__(self):
        try:
            print("\n[Orchestrator] Initializing orchestrator...")
            # Load model configuration
            config_list = self._load_config()
            print(f"[Orchestrator] Loaded model config: {config_list}")
            
            # Initialize agents
            self.planner = PlannerAgent(config_list)
            self.foundation = FoundationAgent(config_list)
            self.interface = InterfaceAgent(config_list)
            self.state_motion = StateMotionAgent(config_list)
            print("[Orchestrator] All agents initialized successfully")
            
            # Ensure generated directory exists
            os.makedirs("generated", exist_ok=True)
            print("[Orchestrator] Generated directory ensured")
        except Exception as e:
            print(f"[Orchestrator] Error in initialization: {str(e)}")
            raise

    @property
    def project_status(self):
        """Access the class-level project status dictionary."""
        return self._project_status

    async def initialize_project(self, project_config: Dict) -> str:
        """Initialize a new project and return its ID."""
        try:
            print("\n[Orchestrator] Starting project initialization...")
            # Convert Pydantic model to dict if needed
            config_dict = project_config.dict() if hasattr(project_config, 'dict') else project_config
            print(f"[Orchestrator] Project config: {config_dict}")
            
            # Generate unique project ID
            project_id = str(uuid.uuid4())
            print(f"[Orchestrator] Generated project ID: {project_id}")
            
            # Initialize project status in class-level dictionary
            self._project_status[project_id] = {
                "project_id": project_id,
                "start_time": datetime.now().isoformat(),
                "status": "initializing",
                "config": config_dict,
                "current_step": "Planning project structure",
                "completed_steps": [],
                "errors": []
            }
            print(f"[Orchestrator] Project status initialized: {self._project_status[project_id]}")
            print(f"[Orchestrator] Current projects in tracking: {list(self._project_status.keys())}")
            
            # Create project directory
            project_dir = os.path.join("generated", project_id)
            os.makedirs(project_dir, exist_ok=True)
            print(f"[Orchestrator] Created project directory: {project_dir}")
            
            return project_id
        except Exception as e:
            print(f"[Orchestrator] Error in project initialization: {str(e)}")
            raise

    async def generate_project(self, project_id: str) -> None:
        """Generate the React project based on configuration."""
        try:
            print(f"\n[Orchestrator] Starting project generation for ID: {project_id}")
            if project_id not in self.project_status:
                raise ValueError(f"Project {project_id} not found")
            
            config = self.project_status[project_id]["config"]
            print(f"[Orchestrator] Using config: {config}")
            
            # Update status
            self.project_status[project_id]["status"] = "in_progress"
            
            # Execute project generation steps
            await self._execute_generation_steps(project_id, config)
            
            # Create ZIP file
            print("[Orchestrator] Creating project ZIP file...")
            self.project_status[project_id]["current_step"] = "Creating project ZIP"
            if await create_project_zip(project_id):
                self.project_status[project_id]["completed_steps"].append("Project ZIP created")
                print("[Orchestrator] Project ZIP created successfully")
            else:
                raise Exception("Failed to create project ZIP file")
            
            # Update final status
            self.project_status[project_id]["status"] = "completed"
            self.project_status[project_id]["current_step"] = "Project generation completed"
            self.project_status[project_id]["completed_steps"].append("Project generation completed")
            print(f"[Orchestrator] Project generation completed for ID: {project_id}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Orchestrator] Error in project generation: {error_msg}")
            self.project_status[project_id]["status"] = "failed"
            self.project_status[project_id]["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "message": error_msg,
                "step": self.project_status[project_id].get("current_step", "unknown")
            })
            raise

    async def get_project_status(self, project_id: str) -> Dict:
        """Get the current status of a project."""
        try:
            print(f"\n[Orchestrator] Getting status for project: {project_id}")
            print(f"[Orchestrator] Current projects in tracking: {list(self._project_status.keys())}")
            
            if project_id not in self._project_status:
                print(f"[Orchestrator] Project {project_id} not found in status tracking")
                raise ValueError(f"Project {project_id} not found")
                
            status = self._project_status[project_id]
            print(f"[Orchestrator] Retrieved status: {status}")
            return status
        except Exception as e:
            print(f"[Orchestrator] Error getting project status: {str(e)}")
            raise

    async def _execute_generation_steps(self, project_id: str, config: Dict) -> None:
        """Execute the project generation steps in sequence."""
        try:
            print(f"\n[Orchestrator] Executing generation steps for project: {project_id}")
            
            # Step 1: Plan project structure
            print("[Orchestrator] Step 1: Planning project structure")
            self.project_status[project_id]["current_step"] = "Planning project structure"
            if await self.planner.plan_project(config, project_id):
                self.project_status[project_id]["completed_steps"].append("Project planning completed")
                print("[Orchestrator] Project planning completed")
            
            # Step 2: Set up project foundation
            print("[Orchestrator] Step 2: Setting up project foundation")
            self.project_status[project_id]["current_step"] = "Setting up project foundation"
            if await self.foundation.initialize_project(config, project_id):
                self.project_status[project_id]["completed_steps"].append("Project foundation setup completed")
                print("[Orchestrator] Project foundation setup completed")
            
            # Step 3: Generate UI components
            print("[Orchestrator] Step 3: Generating UI components")
            self.project_status[project_id]["current_step"] = "Generating UI components"
            if await self.interface.generate_components(config, project_id):
                self.project_status[project_id]["completed_steps"].append("UI components generation completed")
                print("[Orchestrator] UI components generation completed")
            
            # Step 4: Set up state management and animations
            print("[Orchestrator] Step 4: Setting up state management and animations")
            self.project_status[project_id]["current_step"] = "Setting up state management and animations"
            if await self.state_motion.setup_state_management(config, project_id):
                self.project_status[project_id]["completed_steps"].append("State management setup completed")
                print("[Orchestrator] State management setup completed")
                
        except Exception as e:
            error_msg = str(e)
            print(f"[Orchestrator] Error in generation steps: {error_msg}")
            self.project_status[project_id]["status"] = "failed"
            self.project_status[project_id]["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "message": error_msg,
                "step": self.project_status[project_id].get("current_step", "unknown")
            })
            raise

    def _load_config(self) -> list:
        """Load model configuration."""
        try:
            print("\n[Orchestrator] Loading model configuration...")
            # Use DeepSeek Qwen3 8B through OpenRouter
            config = [{
                "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "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"
            }]
            print(f"[Orchestrator] Model configuration loaded: {config}")
            return config
        except Exception as e:
            print(f"[Orchestrator] Error loading configuration: {str(e)}")
            raise 