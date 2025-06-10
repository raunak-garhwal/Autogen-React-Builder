from autogen import AssistantAgent, UserProxyAgent
from typing import Dict, List
import json
import os

class PlannerAgent:
    def __init__(self, config_list):
        try:
            print("\n[Planner] Initializing planner agent...")
            # Initialize the assistant with proper error handling
            self.assistant = AssistantAgent(
                name="planner",
                system_message="""You are a senior software architect specializing in React applications.
                Your role is to break down project requirements into clear, actionable tasks and coordinate with other agents.
                You ensure the project follows best practices and maintains consistency across all components.""",
                llm_config={
                    "config_list": config_list,
                    "temperature": 0.7
                }
            )
            
            # Initialize the user proxy with Docker disabled
            self.user_proxy = UserProxyAgent(
                name="project_manager",
                code_execution_config={
                    "work_dir": "generated",
                    "use_docker": False
                },
                human_input_mode="NEVER"
            )
            print("[Planner] Initialization complete")
        except Exception as e:
            print(f"[Planner] Error in initialization: {str(e)}")
            raise

    async def plan_project(self, project_config: Dict, project_id: str) -> bool:
        """Plan the project structure and create initial plan."""
        try:
            print(f"\n[Planner] Planning project structure for ID: {project_id}")
            # Create project plan
            plan = await self.create_project_plan(project_config)
            print(f"[Planner] Created project plan: {plan}")
            
            # Save plan to project directory
            project_dir = os.path.join("generated", project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            plan_file = os.path.join(project_dir, "project-plan.json")
            with open(plan_file, "w") as f:
                json.dump(plan, f, indent=2)
            print(f"[Planner] Saved project plan to: {plan_file}")
            
            return True
        except Exception as e:
            print(f"[Planner] Error planning project: {str(e)}")
            return False

    async def create_project_plan(self, project_config: Dict) -> List[Dict]:
        """Create a detailed project plan based on the configuration."""
        try:
            print("\n[Planner] Creating project plan...")
            # Convert Pydantic model to dict if needed
            config_dict = project_config.dict() if hasattr(project_config, 'dict') else project_config
            print(f"[Planner] Using config: {config_dict}")
            
            # Convert project config to a clear requirements message
            requirements = self._format_requirements(config_dict)
            print(f"[Planner] Formatted requirements:\n{requirements}")
            
            # Initialize the conversation with the planner
            print("[Planner] Starting conversation with assistant...")
            response = await self.user_proxy.initiate_chat(
                self.assistant,
                message=f"""Please create a detailed project plan for the following requirements:
                {requirements}
                
                Break it down into sequential tasks with clear dependencies.
                Format the response as a list of tasks with phases."""
            )
            print(f"[Planner] Received response from assistant: {response}")
            
            # Extract and structure the plan from the conversation
            plan = self._extract_plan_from_response(self.assistant.last_message())
            print(f"[Planner] Extracted plan: {plan}")
            
            if not plan:
                raise Exception("Failed to generate project plan")
                
            return plan
        except Exception as e:
            print(f"[Planner] Error creating project plan: {str(e)}")
            raise

    def _format_requirements(self, config: Dict) -> str:
        """Format project configuration into a clear requirements string."""
        try:
            print("\n[Planner] Formatting requirements...")
            # Get project name and description with defaults
            project_name = config.get('project_name', 'React App')
            description = config.get('description', 'A React application')
            
            # Get features list with default empty list
            features = config.get('features', [])
            features_str = "\n".join(f"- {feature}" for feature in features) if features else "No additional features specified"
            
            requirements = f"""
            Project Name: {project_name}
            Description: {description}
            
            Features:
            {features_str}
            
            Technical Configuration:
            - React + JavaScript + Vite setup with Tailwind CSS
            - State Management: {'Zustand' if config.get('state_management') else 'None'}
            - Routing: {'Enabled' if config.get('routing') else 'Disabled'}
            - Icons: {'Both lucide-react and react-icons' if config.get('icons') else 'Disabled'}
            - Animations: {'Enabled' if config.get('animations') else 'Disabled'}
            """
            print(f"[Planner] Formatted requirements:\n{requirements}")
            return requirements
        except Exception as e:
            print(f"[Planner] Error formatting requirements: {str(e)}")
            raise

    def _extract_plan_from_response(self, response: str) -> List[Dict]:
        """Extract and structure the project plan from the agent's response."""
        try:
            print("\n[Planner] Extracting plan from response...")
            print(f"[Planner] Raw response: {response}")
            
            tasks = []
            current_phase = None
            
            # Handle None response
            if not response:
                print("[Planner] No response received, using default tasks")
                return self._get_default_tasks()
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Phase'):
                    current_phase = line
                    print(f"[Planner] Found phase: {current_phase}")
                    continue
                    
                if line.startswith('- '):
                    task = {
                        'phase': current_phase or 'Setup',
                        'task': line[2:],
                        'status': 'pending'
                    }
                    tasks.append(task)
                    print(f"[Planner] Added task: {task}")
            
            # Ensure we have at least some tasks
            tasks = tasks if tasks else self._get_default_tasks()
            print(f"[Planner] Final task list: {tasks}")
            return tasks
            
        except Exception as e:
            print(f"[Planner] Error extracting plan: {str(e)}")
            raise

    def _get_default_tasks(self) -> List[Dict]:
        """Get default tasks for the project."""
        print("\n[Planner] Using default tasks")
        tasks = [
            {
                'phase': 'Setup',
                'task': 'Initialize React + TypeScript + Vite project',
                'status': 'pending'
            },
            {
                'phase': 'Setup',
                'task': 'Configure styling solution',
                'status': 'pending'
            },
            {
                'phase': 'Components',
                'task': 'Create base UI components',
                'status': 'pending'
            },
            {
                'phase': 'Features',
                'task': 'Implement core functionality',
                'status': 'pending'
            }
        ]
        print(f"[Planner] Default tasks: {tasks}")
        return tasks

    async def validate_task_completion(self, task: Dict) -> bool:
        """Validate that a task has been completed successfully."""
        try:
            validation_prompt = f"""Please validate the following task has been completed successfully:
            Task: {task['task']}
            Phase: {task['phase']}
            
            Review the implementation and confirm it meets requirements."""
            
            await self.user_proxy.initiate_chat(
                self.assistant,
                message=validation_prompt
            )
            
            # Parse the validation response
            response = self.assistant.last_message().lower()
            return 'success' in response or 'completed' in response
        except Exception as e:
            print(f"Error validating task: {str(e)}")
            return False 