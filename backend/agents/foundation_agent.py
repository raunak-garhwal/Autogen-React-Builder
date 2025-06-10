from autogen import AssistantAgent, UserProxyAgent
from typing import Dict
import json
import os

class FoundationAgent:
    def __init__(self, config_list):
        self.config_list = config_list
        self.assistant = AssistantAgent(
            name="foundation_builder",
            system_message="""You are a React project foundation expert.
            Your role is to set up the initial project structure, configure build tools,
            and establish the base architecture for React applications.""",
            llm_config={"config_list": config_list}
        )
        
        self.user_proxy = UserProxyAgent(
            name="foundation_manager",
            code_execution_config={
                "work_dir": "generated",
                "use_docker": False
            },
            human_input_mode="NEVER"
        )

    async def initialize_project(self, project_config: Dict, project_id: str) -> bool:
        """Initialize a new React project with the specified configuration."""
        
        # Create project directory
        project_dir = os.path.join("generated", project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Convert Pydantic model to dict if needed
        config_dict = project_config if isinstance(project_config, dict) else project_config.dict()
        
        # Generate package.json
        package_json = self._generate_package_json(config_dict)
        
        # Generate tsconfig.json
        tsconfig = self._generate_tsconfig()
        
        # Generate vite.config.ts
        vite_config = self._generate_vite_config(config_dict)
        
        # Write configuration files
        try:
            with open(os.path.join(project_dir, "package.json"), "w") as f:
                json.dump(package_json, f, indent=2)
                
            with open(os.path.join(project_dir, "tsconfig.json"), "w") as f:
                json.dump(tsconfig, f, indent=2)
                
            with open(os.path.join(project_dir, "vite.config.ts"), "w") as f:
                f.write(vite_config)
                
            return True
        except Exception as e:
            print(f"Error initializing project: {str(e)}")
            return False

    def _generate_package_json(self, config: Dict) -> Dict:
        """Generate package.json with required dependencies."""
        package = {
            "name": config["project_name"].lower().replace(" ", "-"),
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.15",
                "@types/react-dom": "^18.2.7",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "@vitejs/plugin-react": "^4.0.3",
                "eslint": "^8.45.0",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.4.3",
                "typescript": "^5.0.2",
                "vite": "^4.4.5"
            }
        }
        
        # Add optional dependencies based on configuration
        if config["styling"] == "tailwind":
            package["devDependencies"]["tailwindcss"] = "^3.3.0"
            package["devDependencies"]["postcss"] = "^8.4.31"
            package["devDependencies"]["autoprefixer"] = "^10.4.16"
            
        if config["state_management"] == "zustand":
            package["dependencies"]["zustand"] = "^4.4.1"
            
        if config["routing"]:
            package["dependencies"]["react-router-dom"] = "^6.15.0"
            
        if config["animations"]:
            package["dependencies"]["framer-motion"] = "^10.16.4"
            
        if config["ui_framework"] == "shadcn":
            package["dependencies"]["@radix-ui/react-slot"] = "^1.0.2"
            package["dependencies"]["class-variance-authority"] = "^0.7.0"
            package["dependencies"]["clsx"] = "^2.0.0"
            package["dependencies"]["tailwind-merge"] = "^1.14.0"
            
        return package

    def _generate_tsconfig(self) -> Dict:
        """Generate tsconfig.json with React + TypeScript configuration."""
        return {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"]
                }
            },
            "include": ["src"],
            "references": [{ "path": "./tsconfig.node.json" }]
        }

    def _generate_vite_config(self, config: Dict) -> str:
        """Generate vite.config.ts with project configuration."""
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})"""

    async def setup_project_structure(self, project_id: str) -> bool:
        """Set up the basic project structure with necessary directories."""
        try:
            project_dir = os.path.join("generated", project_id)
            
            # Create directory structure
            directories = [
                "src",
                "src/components",
                "src/pages",
                "src/hooks",
                "src/utils",
                "src/assets",
                "src/types",
                "public"
            ]
            
            for directory in directories:
                os.makedirs(os.path.join(project_dir, directory), exist_ok=True)
                
            return True
        except Exception as e:
            print(f"Error setting up project structure: {str(e)}")
            return False 