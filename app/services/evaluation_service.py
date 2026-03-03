# @Version :1.0
# @Author  : Mingyue
# @File    : evaluation_service.py.py
# @Time    : 02/03/2026 19:50
import logging
import traceback
import textwrap
import ast
import io
import sys

logger = logging.getLogger(__name__)


def _syntax_check(code: str) -> tuple[bool, str | None]:
    """Check if code has valid Python syntax."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def _safe_exec(code: str) -> tuple[bool, str | None]:
    """
    Execute code in a restricted namespace.
    Matplotlib is patched to non-interactive mode to avoid GUI popups.
    """
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend

    namespace = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "enumerate": enumerate,
            "zip": zip,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "reversed": reversed,
            "isinstance": isinstance,
            "__import__": __import__,
        }
    }

    # Redirect stdout to suppress print output during eval
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(textwrap.dedent(code), namespace)  # noqa: S102
        return True, None
    except Exception as e:
        tb = traceback.format_exc()
        logger.debug(f"Execution error:\n{tb}")
        return False, f"{type(e).__name__}: {e}"
    finally:
        sys.stdout = old_stdout


def _has_matplotlib_output(code: str) -> bool:
    """Check if the code appears to produce a matplotlib figure."""
    keywords = ["plt.", "matplotlib", "fig,", "ax.", "subplot", "figure"]
    return any(kw in code for kw in keywords)


def evaluate_code(code: str) -> dict:
    """
    Evaluate generated code.
    Returns: {result: "correct"|"partially_correct"|"failed", error_message: str|None}
    """
    logger.info("Starting code evaluation")

    if not code or not code.strip():
        return {"result": "failed", "error_message": "Empty code"}

    # Step 1: Syntax check
    syntax_ok, syntax_err = _syntax_check(code)
    if not syntax_ok:
        logger.warning(f"Syntax check failed: {syntax_err}")
        return {"result": "failed", "error_message": syntax_err}

    # Step 2: Execution
    exec_ok, exec_err = _safe_exec(code)
    if not exec_ok:
        logger.warning(f"Execution failed: {exec_err}")
        return {"result": "failed", "error_message": exec_err}

    # Step 3: Quality check
    has_viz = _has_matplotlib_output(code)
    if exec_ok and has_viz:
        return {"result": "correct", "error_message": None}
    elif exec_ok and not has_viz:
        return {"result": "partially_correct", "error_message": "Code ran but no matplotlib output detected"}

    return {"result": "failed", "error_message": exec_err}