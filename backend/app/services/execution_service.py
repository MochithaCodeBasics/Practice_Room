import subprocess
import asyncio
from ..core.config import settings
import tempfile
import os
import uuid
import shutil
import sys
from pathlib import Path
from ..models import ExecutionRequest, ExecutionResult, User

# SECURITY: Import Docker executor for secure execution
from .docker_executor import docker_executor

class ExecutionService:
    def __init__(self):
        # SECURITY: Use Docker-based execution when available
        self.use_docker = os.getenv("USE_DOCKER_EXECUTOR", "true").lower() == "true"
        self.docker_available = docker_executor.is_available() if self.use_docker else False
        
        if self.use_docker and not self.docker_available:
            print("WARNING: Docker execution requested but Docker is not available.")
            print("SECURITY WARNING: Falling back to local execution - this is insecure!")
            print("To fix: Install Docker and build the image with:")
            print("  docker build -t practice-room-python:latest -f docker/Dockerfile.python .")
        
        print(f"DEBUG: ExecutionService initialized. use_docker={self.use_docker}, docker_available={self.docker_available}")

    async def run_code(self, request: ExecutionRequest, question_data: dict, current_user: User) -> ExecutionResult:
        if self.use_docker and self.docker_available:
             # Determine image based on module
             # We need to query the module table. 
             # Since this service is async, we should use a session.
             # However, for MVP, we might optimize or cache this. 
             # For now, let's just do a quick lookup.
             from sqlmodel import Session, select
             from ..database import engine
             from ..models import Module
             
             image_name = "practice-room-python:latest" # Default
             if request.module_id:
                 try:
                     with Session(engine) as session:
                         module = session.get(Module, request.module_id)
                         if module and module.base_image:
                             image_name = module.base_image
                 except Exception as e:
                     print(f"Error fetching module image: {e}")

             print(f"DEBUG: Running code in Docker using image: {image_name}")

             # Pass LLM API KEYS if available
             env_vars = {}
             if current_user.groq_api_key:
                 env_vars["GROQ_API_KEY"] = current_user.groq_api_key.strip()
             if current_user.openai_api_key:
                 env_vars["OPENAI_API_KEY"] = current_user.openai_api_key.strip()
             if current_user.anthropic_api_key:
                 env_vars["ANTHROPIC_API_KEY"] = current_user.anthropic_api_key.strip()
             
             env_vars["DEFAULT_LLM_PROVIDER"] = current_user.default_llm_provider or "groq"

             # SECURITY: Enable network ONLY for GenAI and Agentic modules
             is_ai_module = any(keyword in image_name.lower() for keyword in ["genai", "agentic", "nlp"])
             network_enabled = is_ai_module
             
             if is_ai_module:
                 # Check if at least one key is configured
                 has_any_key = any([current_user.groq_api_key, current_user.openai_api_key, current_user.anthropic_api_key])
                 if not has_any_key:
                    return ExecutionResult(
                        stdout="", 
                        stderr="No service keys configured. Please go to Environment Settings and enter a provider key (Groq, OpenAI, or Anthropic) to use advanced features.",
                        status="error"
                    )

             result = await docker_executor.run_code(
                 request.code, 
                 Path(question_data["folder_path"]),
                 image_name=image_name,
                 timeout=settings.DOCKER_TIMEOUT,
                 env_vars=env_vars,
                 network_enabled=network_enabled
             )
             return result
        else:
            print("DEBUG: Falling back to local execution")
            # Fallback to local execution
            return await self._run_code_local_async(request, question_data, current_user)


    async def _run_code_local_async(self, request: ExecutionRequest, question_data: dict, current_user: User) -> ExecutionResult:
        code = request.code
        
        # Create a temp dir for this run
        run_id = str(uuid.uuid4())
        base_dir = Path("runs").resolve()
        base_dir.mkdir(exist_ok=True)
        work_dir = base_dir / run_id
        work_dir.mkdir()
        
        try:
            # Write user code
            (work_dir / "user_code.py").write_text(code, encoding="utf-8")
            
            # Generic Driver: Runs user code as __main__ and captures plots
            driver_code = """
import sys
import os
import matplotlib
matplotlib.use('Agg') # Force non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import traceback

# Add current dir to path
sys.path.append(os.getcwd())

# Context for execution
global_ns = {
    "__name__": "__main__",
    "__file__": "user_code.py"
}

try:
    # Auto-load data.csv if present
    if os.path.exists("data.csv"):
        try:
            loaded_df = pd.read_csv("data.csv")
            loaded_df.columns = loaded_df.columns.str.lower().str.strip()
            global_ns["data"] = loaded_df
            global_ns["df"] = loaded_df
        except Exception:
            pass

    # Injection: Add get_llm to builtins/global_ns if available
    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
        global_ns["get_llm"] = get_llm
    except ImportError:
        pass

    with open("user_code.py", "r", encoding="utf-8") as f:
        user_source = f.read()
    
    exec(user_source, global_ns)
    
    # Check for plots
    fignums = plt.get_fignums()
    if fignums:
        for i, num in enumerate(fignums):
            fig = plt.figure(num)
            if len(fignums) == 1:
                fname = "output.png"
            else:
                fname = f"output_{i+1}.png"
            
            fig.savefig(fname, bbox_inches='tight')
            plt.close(fig) 
            
except Exception as e:
    traceback.print_exc()
"""
            (work_dir / "main.py").write_text(driver_code, encoding="utf-8")
            
            # Copy data files
            q_dir = Path(question_data["folder_path"])
            
            if q_dir.exists() and q_dir.is_dir():
                parts = q_dir.parts
                if "questions" in parts:
                    idx = parts.index("questions")
                    rel_path = Path(*parts[idx:])
                    target_dir = work_dir / rel_path
                    target_dir.mkdir(parents=True, exist_ok=True)
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, target_dir / f)
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception as copy_err:
                                print(f"DEBUG: Failed to copy file {f}: {copy_err}")
                else:
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception as copy_err:
                                print(f"DEBUG: Failed to copy file {f}: {copy_err}")
            else:
                print(f"DEBUG: Question directory not found: {q_dir}")

            # Injection: Copy _env.py from questions/
            env_file = settings.QUESTIONS_DIR / "_env.py"
            if env_file.exists():
                shutil.copy(env_file, work_dir / "_env.py")

            # Build/Run command using run_in_executor to avoid asyncio subprocess issues on Windows
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            def run_sync():
                return subprocess.run(
                    [sys.executable, "main.py"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30,
                    encoding="utf-8",
                    errors="replace"
                )

            # Inject keys for local run (NEW)
            if current_user.groq_api_key:
                env["GROQ_API_KEY"] = current_user.groq_api_key.strip()
            if current_user.openai_api_key:
                env["OPENAI_API_KEY"] = current_user.openai_api_key.strip()
            if current_user.anthropic_api_key:
                env["ANTHROPIC_API_KEY"] = current_user.anthropic_api_key.strip()
            
            env["DEFAULT_LLM_PROVIDER"] = current_user.default_llm_provider or "groq"

            loop = asyncio.get_running_loop()
            try:
                # Run the blocking subprocess call in a separate thread
                proc = await loop.run_in_executor(None, run_sync)
                stdout = proc.stdout
                stderr = proc.stderr
                return_code = proc.returncode
            except subprocess.TimeoutExpired:
                stdout = ""
                stderr = "Execution timed out (30s limit)"
                return_code = 1
            except Exception as e:
                stdout = ""
                stderr = f"Execution failed: {str(e)}"
                return_code = 1
            
            # Read all generated png artifacts
            artifacts = []
            for f in work_dir.glob("output*.png"):
                artifacts.append(f.name)
            # Sort to ensure consistent order
            artifacts.sort()

            # Truncate output to prevent browser freeze (50KB limit)
            MAX_OUTPUT_SIZE = 50000 
            if len(stdout) > MAX_OUTPUT_SIZE:
                 stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... [Output truncated due to excessive length]"
            
            if len(stderr) > MAX_OUTPUT_SIZE:
                 stderr = stderr[:MAX_OUTPUT_SIZE] + "\n... [Error output truncated due to excessive length]"

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                artifacts=artifacts,
                status="success" if return_code == 0 else "error",
                run_id=run_id
            )

        except Exception as e:
            import traceback
            print(f"DEBUG: Local execution failed: {e}")
            traceback.print_exc()
            return ExecutionResult(stdout="", stderr=f"Backend Execution Error: {str(e)}\n{traceback.format_exc()}", status="error")
        finally:
            pass
    
    # Keeping old synchronous method commented out or removed
    # def _run_code_local(self, ...): ...

    async def validate_code(self, request: ExecutionRequest, question_data: dict, current_user: User) -> ExecutionResult:
        if self.use_docker and self.docker_available:
             # Look up image same as run_code
             from sqlmodel import Session
             from ..database import engine
             from ..models import Module
             
             image_name = "practice-room-python:latest"
             if request.module_id:
                 try:
                     with Session(engine) as session:
                         module = session.get(Module, request.module_id)
                         if module and module.base_image:
                             image_name = module.base_image
                 except Exception:
                     pass

             # Pass LLM API KEYS if available
             env_vars = {}
             if current_user.groq_api_key:
                 env_vars["GROQ_API_KEY"] = current_user.groq_api_key.strip()
             if current_user.openai_api_key:
                 env_vars["OPENAI_API_KEY"] = current_user.openai_api_key.strip()
             if current_user.anthropic_api_key:
                 env_vars["ANTHROPIC_API_KEY"] = current_user.anthropic_api_key.strip()

             env_vars["DEFAULT_LLM_PROVIDER"] = current_user.default_llm_provider or "groq"

             # SECURITY: Enable network ONLY for GenAI and Agentic modules
             is_ai_module = any(keyword in image_name.lower() for keyword in ["genai", "agentic", "nlp"])
             network_enabled = is_ai_module

             if is_ai_module:
                 # Check if at least one key is configured
                 has_any_key = any([current_user.groq_api_key, current_user.openai_api_key, current_user.anthropic_api_key])
                 if not has_any_key:
                     return ExecutionResult(
                         stdout="", 
                         stderr="No service keys configured.",
                         status="error"
                     )

             result = await docker_executor.validate_code(
                 request.code, 
                 Path(question_data["folder_path"]),
                 image_name=image_name, 
                 timeout=settings.DOCKER_TIMEOUT,
                 env_vars=env_vars,
                 network_enabled=network_enabled
             )
             return result
        else:
            # Fallback to local execution
            return await self._validate_code_local_async(request, question_data, current_user)

    async def _validate_code_local_async(self, request: ExecutionRequest, question_data: dict, current_user: User) -> ExecutionResult:

        code = request.code
        run_id = str(uuid.uuid4())
        base_dir = Path("runs").resolve()
        base_dir.mkdir(exist_ok=True)
        work_dir = base_dir / run_id
        work_dir.mkdir()
        
        try:
            # Write user code
            (work_dir / "user_code.py").write_text(code, encoding="utf-8")
            
            # Copy validator
            if "validator_path" in question_data:
                shutil.copy(question_data["validator_path"], work_dir / "validator.py")
            
            # Copy data files (txt, csv, json)
            q_dir = Path(question_data["folder_path"])

            if q_dir.exists() and q_dir.is_dir():
                parts = q_dir.parts
                if "questions" in parts:
                    idx = parts.index("questions")
                    rel_path = Path(*parts[idx:])
                    target_dir = work_dir / rel_path
                    target_dir.mkdir(parents=True, exist_ok=True)
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, target_dir / f)
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception as copy_err:
                                print(f"DEBUG: Failed to copy file {f}: {copy_err}")
                else:
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception as copy_err:
                                print(f"DEBUG: Failed to copy file {f}: {copy_err}")
            else:
                print(f"DEBUG: Question directory not found for validation: {q_dir}")
            
            # Injection: Copy _env.py from questions/
            env_file = settings.QUESTIONS_DIR / "_env.py"
            if env_file.exists():
                shutil.copy(env_file, work_dir / "_env.py")
            
            # Create validation driver
            driver_code = """
import sys
import os
import builtins

# Add current dir to path
sys.path.append(os.getcwd())

# Inject data DataFrame into builtins BEFORE importing user_code
import pandas as pd
if os.path.exists("data.csv"):
    try:
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
    except Exception:
        pass

# Injection: Add get_llm to builtins if available
try:
    from _env import get_llm
    builtins.get_llm = get_llm
except ImportError:
    pass

import validator
import user_code

try:
    result = validator.validate(user_code)
    print(result)
except Exception as e:
    print(f"Validation Wrapper Error: {e}")
"""
            (work_dir / "validate_driver.py").write_text(driver_code, encoding="utf-8")
            
            # Run validation async using run_in_executor
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            def run_sync_validate():
                return subprocess.run(
                    [sys.executable, "validate_driver.py"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30,
                    encoding="utf-8",
                    errors="replace"
                )

            # Inject keys for local validation (NEW)
            if current_user.groq_api_key:
                env["GROQ_API_KEY"] = current_user.groq_api_key.strip()
            if current_user.openai_api_key:
                env["OPENAI_API_KEY"] = current_user.openai_api_key.strip()
            if current_user.anthropic_api_key:
                env["ANTHROPIC_API_KEY"] = current_user.anthropic_api_key.strip()
            
            env["DEFAULT_LLM_PROVIDER"] = current_user.default_llm_provider or "groq"

            loop = asyncio.get_running_loop()
            try:
                proc = await loop.run_in_executor(None, run_sync_validate)
                stdout = proc.stdout
                stderr = proc.stderr
                return_code = proc.returncode
            except subprocess.TimeoutExpired:
                stdout = ""
                stderr = "Validation timed out (30s limit)"
                return_code = 1
            except Exception as e:
                stdout = ""
                stderr = f"Validation Execution failed: {str(e)}"
                return_code = 1

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                status="success" if return_code == 0 else "error",
                run_id=run_id
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ExecutionResult(stdout="", stderr=f"Backend Validation Error: {str(e)}\n{traceback.format_exc()}", status="error")

execution_service = ExecutionService()
execution_service = ExecutionService()
