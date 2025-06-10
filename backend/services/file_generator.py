from typing import Dict, Optional
import os
from jinja2 import Environment, FileSystemLoader, Template

class FileGenerator:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_file(
        self,
        template_name: str,
        output_path: str,
        context: Dict,
        create_dirs: bool = True
    ) -> bool:
        """Generate a file from a template."""
        try:
            # Get template
            template = self.env.get_template(template_name)
            
            # Create output directory if needed
            if create_dirs:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
            # Render and write file
            with open(output_path, "w") as f:
                f.write(template.render(**context))
                
            return True
        except Exception as e:
            print(f"Error generating file {output_path}: {str(e)}")
            return False

    def generate_from_string(
        self,
        template_string: str,
        output_path: str,
        context: Dict,
        create_dirs: bool = True
    ) -> bool:
        """Generate a file from a template string."""
        try:
            # Create template from string
            template = Template(template_string)
            
            # Create output directory if needed
            if create_dirs:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
            # Render and write file
            with open(output_path, "w") as f:
                f.write(template.render(**context))
                
            return True
        except Exception as e:
            print(f"Error generating file {output_path}: {str(e)}")
            return False

    def generate_multiple(
        self,
        templates: Dict[str, Dict],
        base_path: str,
        global_context: Optional[Dict] = None
    ) -> bool:
        """Generate multiple files from templates."""
        try:
            global_context = global_context or {}
            
            for template_name, config in templates.items():
                # Merge global and local context
                context = {**global_context, **(config.get("context", {}))}
                
                # Generate file
                output_path = os.path.join(base_path, config["output_path"])
                
                if not self.generate_file(
                    template_name=template_name,
                    output_path=output_path,
                    context=context
                ):
                    return False
                    
            return True
        except Exception as e:
            print(f"Error generating multiple files: {str(e)}")
            return False

    def copy_static_files(self, source_dir: str, target_dir: str) -> bool:
        """Copy static files from source to target directory."""
        try:
            import shutil
            
            # Create target directory if needed
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy files
            for item in os.listdir(source_dir):
                source = os.path.join(source_dir, item)
                target = os.path.join(target_dir, item)
                
                if os.path.isdir(source):
                    shutil.copytree(source, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, target)
                    
            return True
        except Exception as e:
            print(f"Error copying static files: {str(e)}")
            return False 