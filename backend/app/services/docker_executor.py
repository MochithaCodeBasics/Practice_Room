"""
Docker-based code execution service.
SECURITY: Provides isolated execution environment to prevent RCE attacks.
"""
import docker
import uuid
import shutil
import os
from pathlib import Path
from typing import Optional
from ..models import ExecutionRequest, ExecutionResult

import asyncio
from ..core.config import settings

class DockerExecutor:
    """Secure code execution using Docker containers."""
    
    def __init__(self):
        self.image_name = "practice-room-python:latest"
        self.client = None
        self._init_client()
        # SECURITY FIX: Limit concurrent executions to prevent DoS
        self.semaphore = asyncio.Semaphore(5)
    
    def _init_client(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            print(f"WARNING: Docker not available - {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self.client is not None
    
    async def run_code(self, code: str, work_dir: Path, image_name: str = "practice-room-python:latest", timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False) -> ExecutionResult:
        """
        Execute user code in a secure Docker container.
        """
        async with self.semaphore:
            return await self._run_code_internal(code, work_dir, image_name, timeout, env_vars, network_enabled)

    async def _run_code_internal(self, code: str, work_dir: Path, image_name: str, timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                stdout="",
                stderr="Docker is not available. Code execution disabled for security.",
                status="error"
            )
        
        run_id = str(uuid.uuid4())
        
        # Run blocking Docker call in thread pool to not block event loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self._execute_container(code, work_dir, image_name, timeout, run_id, env_vars, is_validation=False, network_enabled=network_enabled)
        )

    async def _validate_internal(self, code: str, work_dir: Path, image_name: str, timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                stdout="",
                stderr="Docker is not available.",
                status="error"
            )
        
        run_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._execute_container(code, work_dir, image_name, timeout, run_id, env_vars, is_validation=True, network_enabled=network_enabled)
        )

    def _execute_container(self, code: str, work_dir: Path, image_name: str, timeout: int, run_id: str, env_vars: Optional[dict] = None, is_validation: bool = False, network_enabled: bool = False) -> ExecutionResult:
        """Execute code in Docker container with proper setup."""
        actual_work_dir = Path("runs").resolve() / run_id
        actual_work_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            (actual_work_dir / "user_code.py").write_text(code, encoding="utf-8")
            
            if is_validation:
                # Validation Driver
                driver_code = """
import sys
import os
import builtins
import pandas as pd
import warnings

# Suppress harmless library warnings
warnings.simplefilter("ignore")

sys.path.append(os.getcwd())

if os.path.exists("data.csv"):
    try:
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
    except Exception:
        pass

try:
    # Injection: Add get_llm to builtins/global_ns if available
    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
    except Exception as e:
        print(f"DEBUG: Injection failed: {e}")

    import validator
    import user_code
    
    # Validation logic
    result = validator.validate(user_code)
    
    # Auto-print result if it's a DataFrame or just a string
    if result is not None:
        print(result)
except Exception as e:
    print(f"Validation Wrapper Error: {e}")
    import traceback
    traceback.print_exc()
"""
                # Copy validator.py
                val_path = work_dir / "validator.py"
                if val_path.exists():
                    shutil.copy(val_path, actual_work_dir / "validator.py")
                else:
                    return ExecutionResult(stdout="", stderr="Validator script not found in question folder", status="error")
            else:
                # Execution Driver
                driver_code = '''
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import traceback
import warnings

# Suppress harmless library warnings
warnings.simplefilter("ignore")

sys.path.append(os.getcwd())

global_ns = {
    "__name__": "__main__",
    "__file__": "user_code.py"
}

try:
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
    except Exception as e:
        print(f"DEBUG: Injection failed: {e}")

    with open("user_code.py", "r", encoding="utf-8") as f:
        user_source = f.read()
    
    exec(user_source, global_ns)
    
    
    fignums = plt.get_fignums()
    
    fignums = plt.get_fignums()
    if fignums:
        for i, num in enumerate(fignums):
            fig = plt.figure(num)
            fname = "output.png" if len(fignums) == 1 else f"output_{i+1}.png"
            fig.savefig(fname, bbox_inches='tight')
            plt.close(fig)
except Exception as e:
    traceback.print_exc()
'''
            driver_file = "validate_driver.py" if is_validation else "main.py"
            (actual_work_dir / driver_file).write_text(driver_code, encoding="utf-8")
            
            # Copy all relevant files from the question folder (.csv, .txt, .json, .py)
            for f in os.listdir(work_dir):
                if f.endswith((".csv", ".txt", ".json", ".py")) and f != "master_question_list.csv":
                    shutil.copy(work_dir / f, actual_work_dir / f)
            
            # Injection: Copy shared utils from questions/utils/
            utils_dir = work_dir.parent / "utils"
            if utils_dir.exists() and utils_dir.is_dir():
                for f in os.listdir(utils_dir):
                    if f.endswith(".py"):
                        shutil.copy(utils_dir / f, actual_work_dir / f)
            
            # Injection: Copy _env.py from questions/
            env_file = settings.QUESTIONS_DIR / "_env.py"
            if env_file.exists():
                shutil.copy(env_file, actual_work_dir / "_env.py")
            
            # Prepare environment
            container_env = {
                "PYTHONWARNINGS": "ignore",
                "PYTHONIOENCODING": "utf-8"
            }
            if env_vars:
                container_env.update(env_vars)

            # Run container
            container = self.client.containers.run(
                image_name,
                command=["python", "-W", "ignore", "main.py"] if not is_validation else ["python", "-W", "ignore", "validate_driver.py"],
                environment=container_env,
                volumes={str(actual_work_dir): {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace",
                mem_limit=settings.DOCKER_MEMORY_LIMIT,
                memswap_limit=settings.DOCKER_MEMORY_LIMIT,
                cpu_period=100000,
                cpu_quota=50000,
                network_disabled=not network_enabled,
                user="runner",
                detach=True,
                remove=False
            )
            
            try:
                # Wait for completion with timeout
                try:
                    result = container.wait(timeout=timeout)
                    exit_code = result.get('StatusCode', 1)
                except Exception:
                    # On timeout or wait error
                    try:
                        container.kill()
                    except:
                        pass
                    return ExecutionResult(
                        stdout="",
                        stderr=f"Execution timed out after {timeout} seconds",
                        status="error",
                        run_id=run_id
                    )
                
                # Get logs
                stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
                stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
                
                # Check for output artifacts in the actual work directory
                artifacts = []
                for f in actual_work_dir.glob("output*.png"):
                    artifacts.append(f.name)
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
                    status="success" if exit_code == 0 else "error",
                    run_id=run_id
                )
            finally:
                # Cleanup container - Always run
                try:
                    container.remove(force=True)
                except:
                    pass
            
        except docker.errors.ImageNotFound:
            return ExecutionResult(
                stdout="",
                stderr="Docker image not found. Please build with: docker build -t practice-room-python:latest -f docker/Dockerfile.python .",
                status="error",
                run_id=run_id
            )
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"Docker execution error: {str(e)}",
                status="error",
                run_id=run_id
            )
    
    async def validate_code(self, code: str, work_dir: Path, image_name: str = "practice-room-python:latest", timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False) -> ExecutionResult:
        """Execute validation in Docker container."""
        async with self.semaphore:
            return await self._validate_internal(code, work_dir, image_name, timeout, env_vars, network_enabled)


# Singleton instance
docker_executor = DockerExecutor()
