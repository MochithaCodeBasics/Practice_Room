import subprocess
import asyncio
from ..core.config import settings
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
            import logging
            logging.getLogger("execution").warning(
                "Docker execution requested but not available. Falling back to local execution (insecure)."
            )

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
                 # Check for module type keywords in ID (simple heuristic until DB is fully seeded)
                 mod_id = request.module_id.lower()
                 if "genai" in mod_id or "agentic" in mod_id:
                     image_name = "practice-room-genai:latest"
                 elif "nlp" in mod_id:
                     image_name = "practice-room-nlp:latest"
                 elif "cv" in mod_id or "vision" in mod_id:
                     image_name = "practice-room-cv:latest"
                     image_name = "practice-room-cv:latest"
                 else:
                     try:
                         with Session(engine) as session:
                             module = session.get(Module, request.module_id)
                             if module and module.base_image:
                                 image_name = module.base_image
                     except Exception as e:
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
             env_vars["TRANSFORMERS_VERBOSITY"] = "error"

             # SECURITY: Enable network ONLY for GenAI and Agentic modules
             # We also verify against module_id to catch cases where the image is default but the task is AI-heavy
             mod_id_safe = (request.module_id or "").lower()
             is_ai_image = any(keyword in image_name.lower() for keyword in ["genai", "agentic", "nlp", "cv", "vision", "deep", "dl", "ml"])
             is_ai_id = any(keyword in mod_id_safe for keyword in ["genai", "agentic", "nlp", "cv", "vision", "deep", "dl", "ml"])
             
             is_ai_module = is_ai_image or is_ai_id
             is_nlp_only = "nlp" in image_name.lower() and not any(k in image_name.lower() for k in ["genai", "agentic"])
             network_enabled = is_ai_module

             # Use NLP_TIMEOUT for AI modules (including ML/DL training), DOCKER_TIMEOUT for others
             exec_timeout = settings.NLP_TIMEOUT if is_ai_module else settings.DOCKER_TIMEOUT
             use_hf_cache = is_ai_module
 
             # Only GenAI/Agentic (not NLP, ML, or DL) require API keys
             is_genai_only = is_ai_module and not is_nlp_only and not any(k in mod_id_safe for k in ["ml", "dl"])
             if is_genai_only:
                 has_any_key = any([current_user.groq_api_key, current_user.openai_api_key, current_user.anthropic_api_key])
                 if not has_any_key:
                    return ExecutionResult(
                        stdout="",
                        stderr="No service keys configured. Please go to Environment Settings and enter a provider key (Groq, OpenAI, or Anthropic) to use advanced features.",
                        status="error"
                    )

             # CRITICAL: Wrap Docker executor in try-catch with explicit timeout to prevent hangs
             try:
                 result = await asyncio.wait_for(
                     docker_executor.run_code(
                         request.code,
                         Path(question_data["folder_path"]),
                         image_name=image_name,
                         timeout=exec_timeout,
                         env_vars=env_vars,
                         network_enabled=network_enabled,
                         use_hf_cache=use_hf_cache
                     ),
                     timeout=exec_timeout + 5
                 )
                 return result
             except asyncio.TimeoutError:
                 return ExecutionResult(
                     stdout="",
                     stderr="Docker execution timed out. The code took too long to run.",
                     status="error"
                 )
             except Exception as e:
                 return ExecutionResult(
                     stdout="",
                     stderr=f"Docker execution failed: {str(e)}",
                     status="error"
                 )
        else:
            if self.use_docker and not self.docker_available:
                return ExecutionResult(
                    stdout="",
                    stderr="Docker execution is required but Docker is not running on the server.",
                    status="error"
                )
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
            # CRITICAL: Wrap ALL code in try-catch to prevent subprocess crashes
            driver_code = """
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

# print("SYSTEM: Initializing Execution Engine...", flush=True)

# Add current dir to path
sys.path.append(os.getcwd())

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
            # print("SYSTEM: Dataset 'data' loaded.", flush=True)
        except Exception as csv_err:
            # print(f"SYSTEM WARNING: Could not load data.csv: {csv_err}")
            pass

    # Injection: Add get_llm to builtins/global_ns if available
    try:
        from _env import get_llm
        builtins.get_llm = get_llm
        global_ns["get_llm"] = get_llm
    except ImportError:
        pass

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
    
    # Check for plots
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
                        if f.endswith((".csv", ".txt", ".json", ".py")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, target_dir / f)
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception:
                                pass
                else:
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json", ".py")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception:
                                pass
            else:
                pass

            # Injection: Copy _env.py from questions/
            env_file = settings.QUESTIONS_DIR / "_env.py"
            if env_file.exists():
                shutil.copy(env_file, work_dir / "_env.py")

            # Build/Run command using run_in_executor to avoid asyncio subprocess issues on Windows
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            
            # Determine local timeout based on whether it's an AI module
            # This logic needs to be duplicated here as exec_timeout is local to run_code/validate_code
            is_ai_module_local = any(keyword in question_data.get("image_name", "").lower() for keyword in ["genai", "agentic", "nlp", "ml", "dl"])
            local_exec_timeout = settings.NLP_TIMEOUT if is_ai_module_local else settings.DOCKER_TIMEOUT

            def run_sync():
                return subprocess.run(
                    [sys.executable, "main.py"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=local_exec_timeout,
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
                stderr = f"Execution timed out ({local_exec_timeout}s limit)"
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
            return ExecutionResult(stdout="", stderr=f"Backend Execution Error: {str(e)}\n{traceback.format_exc()}", status="error")

    async def validate_code(self, request: ExecutionRequest, question_data: dict, current_user: User) -> ExecutionResult:
        if self.use_docker and self.docker_available:
             # Look up image same as run_code
             from sqlmodel import Session
             from ..database import engine
             from ..models import Module
             
             image_name = "practice-room-python:latest"
             if request.module_id:
                 # Check for module type keywords in ID
                 mod_id = request.module_id.lower()
                 if "genai" in mod_id or "agentic" in mod_id:
                     image_name = "practice-room-genai:latest"
                 elif "nlp" in mod_id:
                     image_name = "practice-room-nlp:latest"
                 elif "cv" in mod_id or "vision" in mod_id:
                     image_name = "practice-room-cv:latest"
                 else:
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
             env_vars["TRANSFORMERS_VERBOSITY"] = "error"

             # SECURITY: Enable network ONLY for GenAI and Agentic modules
             # We also verify against module_id to catch cases where the image is default but the task is AI-heavy
             mod_id_safe = (request.module_id or "").lower()
             is_ai_image = any(keyword in image_name.lower() for keyword in ["genai", "agentic", "nlp", "cv", "vision", "deep", "dl", "ml"])
             is_ai_id = any(keyword in mod_id_safe for keyword in ["genai", "agentic", "nlp", "cv", "vision", "deep", "dl", "ml"])
             
             is_ai_module = is_ai_image or is_ai_id
             is_nlp_only = "nlp" in image_name.lower() and not any(k in image_name.lower() for k in ["genai", "agentic"])
             network_enabled = is_ai_module

             # Use NLP_TIMEOUT for AI modules (including ML/DL training), DOCKER_TIMEOUT for others
             exec_timeout = settings.NLP_TIMEOUT if is_ai_module else settings.DOCKER_TIMEOUT
             use_hf_cache = is_ai_module

             # Only GenAI/Agentic (not NLP, ML, or DL) require API keys
             is_genai_only = is_ai_module and not is_nlp_only and not any(k in mod_id_safe for k in ["ml", "dl"])
             if is_genai_only:
                 has_any_key = any([current_user.groq_api_key, current_user.openai_api_key, current_user.anthropic_api_key])
                 if not has_any_key:
                     return ExecutionResult(
                         stdout="",
                         stderr="No service keys configured. Please go to Environment Settings and enter a provider key.",
                         status="error"
                     )

             # CRITICAL: Wrap Docker executor in try-catch to prevent crashes
             try:
                 result = await docker_executor.validate_code(
                     request.code,
                     Path(question_data["folder_path"]),
                     image_name=image_name,
                     timeout=exec_timeout,
                     env_vars=env_vars,
                     network_enabled=network_enabled,
                     use_hf_cache=use_hf_cache
                 )
                 return result
             # CRITICAL: Fix waiting for validate_code result
             except asyncio.TimeoutError:
                 return ExecutionResult(
                     stdout="",
                     stderr="Validation timed out. The code took too long to validate.",
                     status="error"
                 )
             except Exception as e:
                 return ExecutionResult(
                     stdout="",
                     stderr=f"Docker validation failed: {str(e)}",
                     status="error"
                 )
        else:
            if self.use_docker and not self.docker_available:
                return ExecutionResult(
                    stdout="",
                    stderr="Docker execution is required but Docker is not running on the server.",
                    status="error"
                )
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
            
            # CRITICAL: Wrap the validator import/execution to prevent uncaught exceptions
            # from causing 500 errors. Validators should output validation messages, not raise.
            
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
                            except Exception:
                                pass
                else:
                    for f in os.listdir(q_dir):
                        if f.endswith((".csv", ".txt", ".json")) and f != "master_question_list.csv":
                            try:
                                shutil.copy(q_dir / f, work_dir / f)
                            except Exception:
                                pass
            else:
                pass
            
            # Injection: Copy _env.py from questions/
            env_file = settings.QUESTIONS_DIR / "_env.py"
            if env_file.exists():
                shutil.copy(env_file, work_dir / "_env.py")

            # Injection: Copy _validator_utils.py from questions/
            val_utils_file = settings.QUESTIONS_DIR / "_validator_utils.py"
            if val_utils_file.exists():
                shutil.copy(val_utils_file, work_dir / "_validator_utils.py")
            
            # Create validation driver - CRITICAL: Wrap all exceptions to prevent 500 errors
            driver_code = """
import sys
import os
import builtins
import traceback
import io
import contextlib

# Ensure UTF-8 output (preserve emoji) and flush promptly
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

# Add current dir to path
sys.path.append(os.getcwd())

# print("SYSTEM: Validation Driver Initializing...", flush=True)

# Set non-interactive matplotlib backend BEFORE any other imports
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

# Add current dir to path
sys.path.append(os.getcwd())

# Inject data DataFrame into builtins BEFORE importing user_code
try:
    import pandas as pd
    if os.path.exists("data.csv"):
        loaded_df = pd.read_csv("data.csv")
        loaded_df.columns = loaded_df.columns.str.lower().str.strip()
        builtins.data = loaded_df
        builtins.df = loaded_df
        # print("SYSTEM: Dataset 'data' loaded.")
except Exception as csv_err:
    # print(f"SYSTEM WARNING: Could not load data.csv: {csv_err}")
    pass

# Injection: Add get_llm to builtins if available
try:
    from _env import get_llm
    builtins.get_llm = get_llm
except ImportError:
    pass

# CRITICAL: Wrap ALL validator execution in try-catch to prevent 500 errors
try:
    import validator
    
    # Injection: Add task-specific variables from validator if available
    if hasattr(validator, "get_input_variables"):
        try:
            input_vars = validator.get_input_variables()
            for k, v in input_vars.items():
                setattr(builtins, k, v)
        except Exception as e:
            # print(f"SYSTEM WARNING: Could not inject input variables: {e}")
            pass

    # print("SYSTEM: Loading your code...")
    import user_code
    # print("SYSTEM: User code loaded successfully.", flush=True)
    
    # Force flush to ensure the above appears even if validation hangs
    sys.stdout.flush()
    
    # Silence validator internal prints if any (student prints in user_code already happened during import)
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

except Exception as validate_err:
    # Captures ImportErrors, SyntaxErrors (if not caught by compiler), and Validator crashes
    error_msg = str(validate_err)
    stack = traceback.format_exc()
    print(f"❌ Validation failed: {error_msg}")
    print(f"\\n<<<VALIDATION_RESULT>>>\\n❌ Execution Error")
    if stack:
        print(f"FULL STACK TRACE:\\n{stack}")
"""
            (work_dir / "validate_driver.py").write_text(driver_code, encoding="utf-8")
            
            # Run validation async using run_in_executor
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            # Determine local timeout based on whether it's an AI module
            is_ai_module_local = any(keyword in str(q_dir).lower() for keyword in ["genai", "agentic", "nlp", "ml", "dl"])
            local_exec_timeout = settings.NLP_TIMEOUT if is_ai_module_local else settings.DOCKER_TIMEOUT

            def run_sync_validate():
                return subprocess.run(
                    [sys.executable, "validate_driver.py"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=local_exec_timeout,
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
                stderr = f"Validation timed out ({local_exec_timeout}s limit)"
                return_code = 1
            except Exception as e:
                stdout = ""
                stderr = f"Validation Execution failed: {str(e)}"
                return_code = 1

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
                status="success" if return_code == 0 else "error",
                run_id=run_id
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ExecutionResult(stdout="", stderr=f"Backend Validation Error: {str(e)}\n{traceback.format_exc()}", status="error")

execution_service = ExecutionService()

