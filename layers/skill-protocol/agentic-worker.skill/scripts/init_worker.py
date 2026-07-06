
import os
import shutil
import argparse

def init_worker(project_name: str):
    """Initializes a new agentic worker project from a template."""
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, "..", "templates", "worker_template.py")
    target_dir = os.path.join(os.getcwd(), project_name)
    target_file = os.path.join(target_dir, f"{project_name}_worker.py")

    os.makedirs(target_dir, exist_ok=True)

    try:
        shutil.copy(template_path, target_file)
        with open(target_file, "r+") as f:
            content = f.read()
            # Replace placeholder with actual project name
            content = content.replace("{{PROJECT_NAME}}", project_name)
            f.seek(0)
            f.write(content)
            f.truncate()
        print(f"✅ Created new agentic worker project 
{project_name}
 at 
{target_file}
")
        print(f"Next steps: cd 
{project_name}
 && python3 
{project_name}_worker.py
")
    except FileNotFoundError:
        print(f"Error: Template file not found at 
{template_path}
")
    except Exception as e:
        print(f"Error initializing worker: 
{e}
")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new agentic worker project.")
    parser.add_argument("project_name", type=str, help="Name of the new worker project.")
    args = parser.parse_args()
    init_worker(args.project_name)
