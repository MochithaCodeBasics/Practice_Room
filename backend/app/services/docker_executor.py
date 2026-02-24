"""
Docker-based code execution service.
SECURITY: Provides isolated execution environment to prevent RCE attacks.
"""
import docker
import uuid
import shutil
import os
import time
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
            # Initial perm fix for HF volume
            self._hf_perms_fixed = False
        except Exception:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self.client is not None

    def _fix_volume_permissions(self, volume_name: str):
        """
        One-time fix for named volume permissions.
        Named volumes on Windows/Linux often default to root:root.
        """
        if not self.is_available() or self.client is None or self._hf_perms_fixed:
            return
            
        try:
            # Ensure alpine image exists
            try:
                self.client.images.get("alpine:latest")
            except docker.errors.ImageNotFound:
                self.client.images.pull("alpine:latest")

            # Run a tiny container as root to fix the volume permissions for the 'runner' user (1000)
            self.client.containers.run(
                "alpine",
                command=["sh", "-c", "mkdir -p /data && chown -R 1000:1000 /data && chmod -R 777 /data"],
                volumes={volume_name: {'bind': '/data', 'mode': 'rw'}},
                remove=True,
                user="root"
            )
            self._hf_perms_fixed = True
        except Exception:
            pass
    
    async def run_code(self, code: str, work_dir: Path, image_name: str = "practice-room-python:latest", timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False, use_hf_cache: bool = False) -> ExecutionResult:
        """
        Execute user code in a secure Docker container.
        """
        async with self.semaphore:
            return await self._run_code_internal(code, work_dir, image_name, timeout, env_vars, network_enabled, use_hf_cache)

    async def _run_code_internal(self, code: str, work_dir: Path, image_name: str, timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False, use_hf_cache: bool = False) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                stdout="",
                stderr="Docker is not available. Code execution disabled for security.",
                status="error"
            )

        # Run Docker calls in thread pool to not block event loop
        run_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._execute_container(code, work_dir, image_name, timeout, run_id, env_vars, is_validation=False, network_enabled=network_enabled, use_hf_cache=use_hf_cache)
                ),
                timeout=timeout + 15
            )
        except asyncio.TimeoutError:
            return ExecutionResult(
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                status="error",
                run_id=run_id
            )

    async def _validate_internal(self, code: str, work_dir: Path, image_name: str, timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False, use_hf_cache: bool = False) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                stdout="",
                stderr="Docker is not available.",
                status="error"
            )

        # Run Docker calls in thread pool
        run_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._execute_container(code, work_dir, image_name, timeout, run_id, env_vars, is_validation=True, network_enabled=network_enabled, use_hf_cache=use_hf_cache)
                ),
                timeout=timeout + 15
            )
        except asyncio.TimeoutError:
            return ExecutionResult(
                stdout="",
                stderr=f"Validation timed out after {timeout} seconds",
                status="error",
                run_id=run_id
            )

    def _execute_container(self, code: str, work_dir: Path, image_name: str, timeout: int, run_id: str, env_vars: Optional[dict] = None, is_validation: bool = False, network_enabled: bool = False, use_hf_cache: bool = False) -> ExecutionResult:
        """Execute code in Docker container with proper setup."""
        actual_work_dir = Path("runs").resolve() / run_id
        actual_work_dir.mkdir(parents=True, exist_ok=True)
        
        # Blocking call: Fix volume permissions if needed
        # This is now safe because we are inside run_in_executor thread
        if use_hf_cache:
            self._fix_volume_permissions(settings.DOCKER_HF_CACHE_VOLUME)
        
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
import io
import contextlib
import traceback

# Ensure UTF-8 output (preserve emoji) and flush promptly
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

# Add current dir to path
sys.path.append(os.getcwd())

# print("SYSTEM: Validation Driver (Docker) Initializing...", flush=True)

# Set non-interactive matplotlib backend BEFORE any other imports
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

if os.path.exists("data.csv"):
    try:
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
        # print("SYSTEM: Dataset 'data' loaded.", flush=True)
    except Exception:
        pass

try:
    # Injection: Add get_llm to builtins/global_ns if available
    try:
        from _env import get_llm
        import builtins
        builtins.get_llm = get_llm
    except Exception as e:
        pass  # get_llm not available in this image

    import validator
    
    # Injection: Add task-specific variables from validator if available
    if hasattr(validator, "get_input_variables"):
        try:
            input_vars = validator.get_input_variables()
            for k, v in input_vars.items():
                setattr(builtins, k, v)
        except Exception as e:
            # print(f"SYSTEM WARNING: Could not inject input variables: {e}", flush=True)
            pass

    # print("SYSTEM: Loading your code...", flush=True)
    sys.stdout.flush()
    import user_code
    # print("SYSTEM: User code loaded successfully.", flush=True)
    sys.stdout.flush()
    
    # Silence validator internal prints if any
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # Call validator with maximum error handling
        try:
            result = validator.validate(user_code)
        except TypeError:
            # Handle cases where validator signature mismatches
            result = validator.validate(user_code, None, None)
    
    # Prefix validation result to separate from stdout
    print(f"\\n<<<VALIDATION_RESULT>>>\\n{result}", flush=True)
except Exception as e:
    error_msg = str(e)
    stack = traceback.format_exc()
    print(f"❌ Validation failed: {error_msg}", flush=True)
    print(f"\\n<<<VALIDATION_RESULT>>>\\n❌ Execution Error", flush=True)
    if stack:
        print(f"FULL STACK TRACE:\\n{stack}", flush=True)
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
import builtins

# Ensure UTF-8 output (preserve emoji) and flush promptly
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

# print("SYSTEM: Initializing Docker Execution Engine...", flush=True)

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
            # print("SYSTEM: Dataset 'data' loaded.", flush=True)
        except Exception:
            pass

    # Injection: Add get_llm to builtins/global_ns if available
    try:
        from _env import get_llm
        builtins.get_llm = get_llm
        global_ns["get_llm"] = get_llm
    except Exception as e:
        pass  # get_llm not available in this image

    # Injection: Add task-specific variables from validator if available
    try:
        import validator
        if hasattr(validator, "get_input_variables"):
            input_vars = validator.get_input_variables()
            for k, v in input_vars.items():
                global_ns[k] = v
                setattr(builtins, k, v)
    except Exception:
        pass

    # print("SYSTEM: Running your code...", flush=True)
    sys.stdout.flush()

    with open("user_code.py", "r", encoding="utf-8") as f:
        user_source = f.read()
    
    exec(user_source, global_ns)
    
    fignums = plt.get_fignums()
    if fignums:
        for i, num in enumerate(fignums):
            fig = plt.figure(num)
            fname = "output.png" if len(fignums) == 1 else f"output_{i+1}.png"
            fig.savefig(fname, bbox_inches='tight')
            plt.close(fig)
except Exception as e:
    print(f"❌ Execution failed: {str(e)}", flush=True)
    traceback.print_exc()
'''
            driver_file = "validate_driver.py" if is_validation else "main.py"
            (actual_work_dir / driver_file).write_text(driver_code, encoding="utf-8")
            
            # Copy all relevant files from the question folder (.csv, .txt, .json, .py)
            for f in os.listdir(work_dir):
                if f.endswith((".csv", ".txt", ".json", ".py", ".pt")) and f != "master_question_list.csv":
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

            # Injection: Copy _validator_utils.py from questions/
            val_utils_file = settings.QUESTIONS_DIR / "_validator_utils.py"
            if val_utils_file.exists():
                shutil.copy(val_utils_file, actual_work_dir / "_validator_utils.py")
            
            # Prepare environment
            container_env = {
                "PYTHONWARNINGS": "ignore",
                "PYTHONIOENCODING": "utf-8",
                "TRANSFORMERS_VERBOSITY": "error",
                "HOME": "/tmp",                        # Force default caches (.cache, .config) to writable /tmp
                "MPLCONFIGDIR": "/tmp/matplotlib",     # Explicit Matplotlib path
                "HF_HUB_DISABLE_SYMLINKS": "1"         # CRITICAL: Fixes PermissionError in Docker volumes
            }
            if env_vars:
                container_env.update(env_vars)

            # Prepare volumes
            container_volumes = {str(actual_work_dir): {'bind': '/workspace', 'mode': 'rw'}}
            if use_hf_cache:
                # Mount persistent cache volume for any new model downloads
                container_volumes[settings.DOCKER_HF_CACHE_VOLUME] = {'bind': '/cache', 'mode': 'rw'}
                if "nlp" in image_name.lower():
                    # NLP image has pre-baked models at /opt/hf_cache
                    container_env["HF_HOME"] = "/opt/hf_cache"
                elif "genai" in image_name.lower():
                     # GenAI image has pre-baked validator model at /opt/genai_cache
                     container_env["HF_HOME"] = "/cache"
                     container_env["SENTENCE_TRANSFORMERS_HOME"] = "/opt/genai_cache"
                else:
                    # Fallback/Agentic/Base Python use the persistent volume for model caching
                    container_env["HF_HOME"] = "/cache"
                    container_env["SENTENCE_TRANSFORMERS_HOME"] = "/cache/sentence_transformers"
                
            # Check if image exists before running
            try:
                self.client.images.get(image_name)
            except docker.errors.ImageNotFound:
                try:
                    self.client.images.pull(image_name)
                except Exception as pull_err:
                    return ExecutionResult(stdout="", stderr=f"Failed to pull Docker image: {pull_err}", status="error", run_id=run_id)
            
            try:
                # Convert memory string (e.g., "2g") to bytes safely
                mem_limit_str = settings.DOCKER_MEMORY_LIMIT.lower() # "2g"
                mem_limit_bytes = 2 * 1024**3 # Default 2GB
                if "g" in mem_limit_str:
                    try:
                        mem_limit_bytes = int(float(mem_limit_str.replace("g", "")) * 1024**3)
                    except ValueError:
                        pass
                elif "m" in mem_limit_str:
                    try:
                        mem_limit_bytes = int(float(mem_limit_str.replace("m", "")) * 1024**2)
                    except ValueError:
                        pass
                
                # print(f"DEBUG: Using safe memory limit: {mem_limit_bytes} bytes", flush=True)

                container = self.client.containers.run(
                    image_name,
                    command=["python", "-W", "ignore", "main.py"] if not is_validation else ["python", "-W", "ignore", "validate_driver.py"],
                    environment=container_env,
                    volumes=container_volumes,
                    working_dir="/workspace",
                    mem_limit=mem_limit_bytes, 
                    # memswap_limit=mem_limit_bytes, # Kept disabled on Windows to prevent potential swap errors
                    # cpu_period=100000, # Disabled for stability
                    # cpu_quota=200000, # Disabled for stability
                    network_disabled=not network_enabled,
                    user="runner",
                    detach=True
                )
            except Exception as run_err:
                 return ExecutionResult(stdout="", stderr=f"Failed to start Docker container: {run_err}", status="error", run_id=run_id)
            
            try:
                # Wait for completion with reliable polling-based timeout
                deadline = time.monotonic() + timeout
                exit_code = None
                
                while time.monotonic() < deadline:
                    try:
                        container.reload()
                        if container.status in ("exited", "dead"):
                            exit_code = container.attrs.get("State", {}).get("ExitCode", 1)
                            break
                    except Exception:
                        pass
                    time.sleep(0.5)

                if exit_code is None:
                    # Timed out - kill the container
                    try:
                        container.stop(timeout=2)
                    except Exception:
                        try:
                            container.kill()
                        except Exception:
                            pass
                    return ExecutionResult(
                        stdout="",
                        stderr=f"Execution timed out after {timeout} seconds",
                        status="error",
                        run_id=run_id
                    )
                
                if exit_code == 137:
                    return ExecutionResult(
                        stdout="",
                        stderr="Execution was killed due to Memory Limit Exceeded (OOM). Try optimizing your code or requesting more memory.",
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
                
                # Parse validation output from stdout
                validation_output = None
                delimiter = "<<<VALIDATION_RESULT>>>"
                
                if delimiter in stdout:
                    parts = stdout.split(delimiter)
                    stdout = parts[0].strip()
                    validation_output = parts[1].strip() if len(parts) > 1 else ""

                return ExecutionResult(
                    stdout=stdout,
                    stderr=stderr,
                    validation_output=validation_output,
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
    
    async def validate_code(self, code: str, work_dir: Path, image_name: str = "practice-room-python:latest", timeout: int = 30, env_vars: Optional[dict] = None, network_enabled: bool = False, use_hf_cache: bool = False) -> ExecutionResult:
        """Execute validation in Docker container."""
        async with self.semaphore:
            return await self._validate_internal(code, work_dir, image_name, timeout, env_vars, network_enabled, use_hf_cache)


# Singleton instance
docker_executor = DockerExecutor()
