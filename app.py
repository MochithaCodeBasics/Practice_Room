import os
import types
import inspect
import importlib
import io
import contextlib

import streamlit as st
import pandas as pd
from streamlit_ace import st_ace

from assests import cb_logo as CB_LOGO
from questions import _env


# ----------------------------
# ⚙️ Page Config
# ----------------------------
page_title = "Codebasics Data Practice Platform"
page_heading = "Python Practice Room"

st.set_page_config(
    page_title=page_title,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# 🎨 Custom CSS
# ----------------------------
st.markdown(
    """
<style>
body {
    background-color: #f8f9fb;
    color: #222;
    font-family: 'Inter', sans-serif;
}
.question-box {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.editor-box {
    background-color: #ffffff;
    padding: 1rem 1.5rem;
    border-radius: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.block-container { padding-top: 0.3rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# 🧭 Header (Sticky)
# ----------------------------
st.markdown(
    f"""
<div style="
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: #0e1117;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 15px;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #2b2b2b;
">
    <img src="{CB_LOGO}" alt="Codebasics Logo" style="width:85px;">
    <h1 style="
        color: white;
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
    ">{page_heading}</h1>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# 📘 Load Master Question List
# ----------------------------
try:
    questions_meta = pd.read_csv("questions/master_question_list.csv")
    questions_meta = questions_meta[questions_meta["active"] == True]
except FileNotFoundError:
    st.error("❌ master_question_list.csv not found in /questions directory.")
    st.stop()

# ----------------------------
# 🧭 Sidebar Filters
# ----------------------------
st.sidebar.header("🔍 Question Selector")

selected_difficulty = st.sidebar.selectbox(
    "🎯 Difficulty", ["All"] + sorted(questions_meta["difficulty"].unique())
)
selected_topic = st.sidebar.selectbox(
    "📘 Topic", ["All"] + sorted(questions_meta["topic"].unique())
)

filtered = questions_meta[
    ((questions_meta["difficulty"] == selected_difficulty) | (selected_difficulty == "All"))
    & ((questions_meta["topic"] == selected_topic) | (selected_topic == "All"))
]

if not filtered.empty:
    selected_title = st.sidebar.selectbox(
        "🧩 Select a Question",
        filtered["title"].tolist(),
        index=0,
        key="question_selector",
    )
    selected_folder = filtered.loc[filtered["title"] == selected_title, "folder_name"].iloc[0]
else:
    st.sidebar.warning("⚠️ No questions available for the selected filters.")
    selected_title, selected_folder = None, None


def _safe_import(module_path: str):
    """Import + reload a module so edits reflect after container restart/rerun."""
    mod = importlib.import_module(module_path)
    try:
        mod = importlib.reload(mod)
    except Exception:
        pass
    return mod


def _detect_question_type(folder: str):
    """
    DATAFRAME question if data.csv exists.
    expected.csv is optional (some DF questions may validate differently).
    FUNCTION question otherwise.
    """
    base = f"questions/{folder}"
    data_path = os.path.join(base, "data.csv")
    expected_path = os.path.join(base, "expected.csv")
    has_data = os.path.exists(data_path)
    has_expected = os.path.exists(expected_path)
    qtype = "dataframe" if has_data else "function"
    return qtype, data_path, expected_path, has_expected


def _build_sandbox_env(data_df=None):
    sandbox_env = vars(_env).copy()
    sandbox_env.update(
        {
            "__name__": "__main__",
            "__builtins__": __builtins__,
        }
    )
    if data_df is not None:
        sandbox_env["data"] = data_df.copy()
    return sandbox_env


def _find_user_dataframe(sandbox_env: dict, original_data: pd.DataFrame | None):
    """
    Priority:
    1) `result` if DataFrame/Series
    2) Modified `data`
    3) Any other DataFrame/Series created by user
    """
    def is_tabular(x):
        t = getattr(x, "__class__", None)
        n = getattr(t, "__name__", "")
        return n in ("DataFrame", "Series")

    user_output = None

    # 1) Explicit result
    if "result" in sandbox_env and is_tabular(sandbox_env["result"]):
        user_output = sandbox_env["result"]

    # 2) Modified data
    if (
        user_output is None
        and original_data is not None
        and "data" in sandbox_env
        and is_tabular(sandbox_env["data"])
    ):
        try:
            if not original_data.equals(sandbox_env["data"]):
                user_output = sandbox_env["data"]
        except Exception:
            user_output = sandbox_env["data"]

    # 3) Any other tabular variable
    if user_output is None:
        for var_name, val in sandbox_env.items():
            if (
                is_tabular(val)
                and var_name not in ["data", "expected", "result"]
                and not var_name.startswith("_")
            ):
                user_output = val
                break

    # Normalize Series -> DataFrame
    if user_output is not None and getattr(user_output.__class__, "__name__", "") == "Series":
        user_output = (
            user_output.to_frame(name=getattr(user_output, "name", None) or "value")
            .reset_index(drop=True)
        )

    return user_output


def _call_validator(v_module, user_module=None, user_df=None, expected_path=None):
    """
    Supports both validator signatures:
    - validate(user_df: pd.DataFrame, expected_path: str) -> str
    - validate(user_module) -> str
    """
    if not hasattr(v_module, "validate"):
        return "⚠️ Validation error: validator.py must define a validate(...) function."

    validate_fn = v_module.validate
    try:
        sig = inspect.signature(validate_fn)
        nparams = len(sig.parameters)
    except Exception:
        nparams = None

    # Prefer signature-based routing
    try:
        if nparams == 1:
            return validate_fn(user_module)
        elif nparams == 2:
            return validate_fn(user_df, expected_path)
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"

    # Fallback routing (best-effort)
    try:
        if user_df is not None and expected_path is not None:
            return validate_fn(user_df, expected_path)
        return validate_fn(user_module)
    except Exception as e:
        return f"⚠️ Validation error: {str(e)}"


# ----------------------------
# 🧠 Load Question Module
# ----------------------------
if not selected_folder:
    st.info("👈 Use the sidebar to select a question and start practicing!")
    st.stop()

qtype, data_path, expected_path, has_expected = _detect_question_type(selected_folder)

try:
    q_module = _safe_import(f"questions.{selected_folder}.question")
    v_module = _safe_import(f"questions.{selected_folder}.validator")

    data = None
    if qtype == "dataframe":
        if not os.path.exists(data_path):
            st.error("❌ data.csv is missing for this dataframe-based question.")
            st.stop()
        data = pd.read_csv(data_path)

    # Inject env objects into question module
    for name in getattr(_env, "__all__", []):
        setattr(q_module, name, getattr(_env, name))

    # Inject data only for dataframe questions
    if data is not None:
        setattr(q_module, "data", data)

    desc = q_module.get_description()
    hint = q_module.get_hint()
    sample_code = q_module.get_inital_sample_code()

except Exception as e:
    st.error(f"❌ Failed to load question module: {e}")
    st.stop()

# ----------------------------
# 🧩 Layout Split
# ----------------------------
col1, col2 = st.columns([1.2, 1.8], gap="medium")

# ----------------------------
# 📗 LEFT PANEL – Question & Dataset
# ----------------------------
with col1:
    st.markdown(f"### 🧠 {selected_title}")
    st.markdown(desc, unsafe_allow_html=True)

    with st.expander("💡 Hint"):
        st.write(hint)

    if qtype == "dataframe":
        st.markdown("### 📊 Dataset Preview")
        st.dataframe(data.head(), use_container_width=True)

        # Optional expected preview (only if expected.csv exists)
        if has_expected:
            try:
                expected_df = pd.read_csv(expected_path)
                preview_df = expected_df.sample(frac=0.7, random_state=42).head(5)

                # Light obfuscation for numeric/object columns (optional)
                for col in preview_df.select_dtypes(include="number").columns:
                    preview_df[col] = preview_df[col] * 1.05
                    preview_df[col] = preview_df[col].apply(
                        lambda x: int(x) if float(x).is_integer() else round(x, 0)
                    )
                for col in preview_df.select_dtypes(include="object").columns:
                    preview_df[col] = preview_df[col].astype(str).str.replace("e", "E", case=False)

                st.markdown("### 🔍 Sample Output Preview (for reference)")
                st.caption("⚠️ Note: This is only an illustrative preview — actual output may differ.")
                st.dataframe(preview_df, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load output preview: {str(e)}")
    else:
        st.info("This is a function-based question. No dataset file is required.")

# ----------------------------
# 💻 RIGHT PANEL – Editor & Output
# ----------------------------
with col2:
    st.markdown("### 💻 Your Code")

    if qtype == "dataframe":
        st.markdown("💡 **Tip:** Use `result` (recommended) or modify `data` to return your final output.")
    else:
        st.markdown("💡 **Tip:** Define the required function exactly as asked (name + behavior).")

    user_code = st_ace(
        value=sample_code,
        language="python",
        theme="github",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        height=350,
        auto_update=True,
        wrap=True,
    )

    btn_col1, btn_col2 = st.columns([1, 1])
    run_clicked = btn_col1.button("▶️ Run Code", use_container_width=True, key="run")
    submit_clicked = btn_col2.button("✅ Submit Code", use_container_width=True, key="submit")

    # ----------------------------
    # ▶️ Run Code (NOW captures print output)
    # ----------------------------
    if run_clicked:
        try:
            sandbox_env = _build_sandbox_env(data_df=data if qtype == "dataframe" else None)

            stdout_buffer = io.StringIO()
            with contextlib.redirect_stdout(stdout_buffer):
                exec(user_code, sandbox_env)

            printed_output = stdout_buffer.getvalue()

            if printed_output.strip():
                st.markdown("### 🖨️ Console Output")
                st.code(printed_output)

            if qtype == "dataframe":
                user_output = _find_user_dataframe(sandbox_env, original_data=data)
                if user_output is not None:
                    st.markdown("### 🧾 Your Output")
                    st.dataframe(user_output, use_container_width=True)
                else:
                    st.warning("⚠️ No DataFrame found in your output.")
            else:
                st.success("✅ Code executed. Now click **Submit Code** to run hidden test cases.")

        except Exception as e:
            st.error(f"Execution error: {str(e)}")

    # ----------------------------
    # ✅ Submit Code (also captures print output)
    # ----------------------------
    if submit_clicked:
        try:
            sandbox_env = _build_sandbox_env(data_df=data if qtype == "dataframe" else None)

            # Backward compatibility
            if has_expected:
                try:
                    sandbox_env["expected"] = pd.read_csv(expected_path)
                except Exception:
                    sandbox_env["expected"] = None
            else:
                sandbox_env["expected"] = None

            stdout_buffer = io.StringIO()
            with contextlib.redirect_stdout(stdout_buffer):
                exec(user_code, sandbox_env)

            printed_output = stdout_buffer.getvalue()
            if printed_output.strip():
                st.markdown("### 🖨️ Console Output")
                st.code(printed_output)

            if qtype == "dataframe":
                user_output = _find_user_dataframe(sandbox_env, original_data=data)
                if user_output is None:
                    st.warning("⚠️ No DataFrame found in your output.")
                else:
                    result_msg = _call_validator(
                        v_module=v_module,
                        user_df=user_output,
                        expected_path=expected_path,
                    )
                    if "✅" in result_msg:
                        st.balloons()
                        st.success("🎉 Great job! Your final submission passed all tests.")
                    else:
                        st.error("❌ Not quite right yet. Try again.")
                    st.caption("Validator feedback:")
                    st.code(result_msg)
                    st.dataframe(user_output, use_container_width=True)

            else:
                user_module = types.SimpleNamespace(**sandbox_env)
                result_msg = _call_validator(v_module=v_module, user_module=user_module)

                if "✅" in result_msg:
                    st.balloons()
                    st.success("🎉 Great job! Your final submission passed all tests.")
                else:
                    st.error("❌ Not quite right yet. Try again.")
                st.caption("Validator feedback:")
                st.code(result_msg)

        except Exception as e:
            st.error(f"Execution error: {str(e)}")
