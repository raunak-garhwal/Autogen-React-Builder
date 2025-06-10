import os
import zipfile
from typing import List, Optional

async def create_project_zip(project_id: str, exclude_patterns: Optional[List[str]] = None) -> bool:
    """Create a ZIP archive of the generated project."""
    try:
        project_dir = os.path.join("generated", project_id)
        zip_path = os.path.join("generated", f"{project_id}.zip")
        
        # Default exclude patterns
        exclude_patterns = exclude_patterns or [
            "__pycache__",
            "*.pyc",
            "node_modules",
            ".git",
            ".env",
            "*.log",
            "status.json"
        ]
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(project_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(
                    pattern in d for pattern in exclude_patterns if "*" not in pattern
                )]
                
                for file in files:
                    # Skip excluded files
                    if any(pattern in file for pattern in exclude_patterns):
                        continue
                        
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, project_dir)
                    
                    try:
                        zf.write(file_path, arc_path)
                    except Exception as e:
                        print(f"Error adding file {file_path} to ZIP: {str(e)}")
                        continue
                        
        return True
    except Exception as e:
        print(f"Error creating ZIP archive: {str(e)}")
        return False

async def extract_project_zip(project_id: str, target_dir: Optional[str] = None) -> bool:
    """Extract a project ZIP archive."""
    try:
        zip_path = os.path.join("generated", f"{project_id}.zip")
        target_dir = target_dir or os.path.join("generated", project_id)
        
        # Create target directory if needed
        os.makedirs(target_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
            
        return True
    except Exception as e:
        print(f"Error extracting ZIP archive: {str(e)}")
        return False

async def get_zip_contents(project_id: str) -> List[str]:
    """Get a list of files in a project ZIP archive."""
    try:
        zip_path = os.path.join("generated", f"{project_id}.zip")
        
        with zipfile.ZipFile(zip_path, "r") as zf:
            return zf.namelist()
    except Exception as e:
        print(f"Error reading ZIP contents: {str(e)}")
        return []

async def get_zip_size(project_id: str) -> int:
    """Get the size of a project ZIP archive in bytes."""
    try:
        zip_path = os.path.join("generated", f"{project_id}.zip")
        return os.path.getsize(zip_path)
    except Exception as e:
        print(f"Error getting ZIP size: {str(e)}")
        return 0