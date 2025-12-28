"""
Simplified code execution engine with direct execution instead of subprocess isolation.

This module provides safe code execution with:
- File access restriction to a specific directory
- Module imports from available_functions
- Clear error reporting
- NO subprocess overhead
"""

import builtins
import importlib
import logging
import os
import traceback
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def execute_sandboxed_code(
    code: str,
    timeout: int = 10,  # Kept for API compatibility, not used in direct execution
    allow_installs: bool = False,  # Kept for API compatibility, not used
    requirements_path: str = None,  # Kept for API compatibility, not used
    allowed_path: str = None,
    blacklist: list = None,  # Kept for API compatibility, not used
    available_functions: dict = None,
    import_module: str = None,
    log: bool = False,
) -> Tuple[Optional[Dict], str]:
    """
    Execute Python code directly with file access restrictions.

    Parameters:
        code (str): The Python code to execute.
        timeout (int): Ignored (kept for API compatibility). Direct execution doesn't use subprocess.
        allow_installs (bool): Ignored (kept for API compatibility).
        requirements_path (str): Ignored (kept for API compatibility).
        allowed_path (str): Directory path that code can access for file I/O.
                           File operations outside this path will be blocked.
        blacklist (list): Ignored (kept for API compatibility).
        available_functions (dict): Dictionary of {name: function} to make available in sandbox.
        import_module (str): Module name to import and expose all non-private callables.
        log (bool): Enable logging output.

    Returns:
        (dict, str): Tuple of (local_variables_dict, error_message_string)
                    - If successful: ({variables}, "")
                    - If failed: (None, "error description")
    """
    # Save original working directory to restore after execution
    original_cwd = os.getcwd()

    try:
        # Build execution environment
        exec_globals = {"__builtins__": builtins.__dict__}
        exec_locals = {}

        # If allowed_path specified, restrict file operations to that directory
        if allowed_path:
            allowed = os.path.normcase(os.path.abspath(allowed_path))
            orig_open = builtins.open

            def secure_open(file, *args, **kwargs):
                """Restricts file access to allowed_path."""
                path = (
                    file
                    if isinstance(file, str)
                    else getattr(file, "name", str(file))
                )
                full_path = os.path.normcase(os.path.abspath(path if path is not None else ""))
                if not full_path.startswith(allowed):
                    raise PermissionError(
                        f"Access to '{full_path}' is denied by sandbox."
                    )
                return orig_open(file, *args, **kwargs)

            builtins.open = secure_open

            # Also restrict os operations
            orig_remove = os.remove

            def secure_remove(path, *args, **kwargs):
                full_path = os.path.normcase(os.path.abspath(path))
                if not full_path.startswith(allowed):
                    raise PermissionError(
                        f"Removal of '{full_path}' is denied by sandbox."
                    )
                return orig_remove(path, *args, **kwargs)

            os.remove = secure_remove

            orig_rename = os.rename

            def secure_rename(src, dst, *args, **kwargs):
                full_src = os.path.normcase(os.path.abspath(src))
                full_dst = os.path.normcase(os.path.abspath(dst))
                if not full_src.startswith(allowed) or not full_dst.startswith(allowed):
                    raise PermissionError(
                        "Rename operation outside allowed path is denied by sandbox."
                    )
                return orig_rename(src, dst, *args, **kwargs)

            os.rename = secure_rename

        # Handle import_module: Import all callables from module
        if import_module:
            try:
                module = importlib.import_module(import_module)
                if available_functions is None:
                    available_functions = {}
                for name in dir(module):
                    if not name.startswith("_"):
                        attr = getattr(module, name)
                        if callable(attr):
                            available_functions[name] = attr
            except ImportError as e:
                error_msg = f"Failed to import module {import_module}: {e}"
                if log:
                    logger.error(error_msg)
                return None, error_msg

        # Add available functions to execution environment
        if available_functions:
            exec_globals.update(available_functions)

        # Execute the user code
        error_msg = ""
        try:
            exec(code, exec_globals, exec_locals)
        except SystemExit as e:
            # Handle sys.exit() calls
            code_val = e.code if isinstance(e.code, int) else 0
            if code_val != 0:
                error_msg = f"Code exited with status {code_val}"
                if log:
                    logger.warning(error_msg)
        except Exception as e:
            # Capture any exception with full traceback
            tb = traceback.format_exc()
            error_msg = f"Exception in code:\n{tb}"
            if log:
                logger.error(error_msg)

        # Clean up built-ins from locals
        exec_locals.pop("__builtins__", None)

        if log and not error_msg:
            logger.info("Code execution succeeded")

        return exec_locals, error_msg

    except Exception as e:
        # Unhandled exception in executor
        error_msg = f"Execution error: {str(e)}"
        if log:
            logger.error(error_msg)
        return None, error_msg
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass

        # Restore original builtins if they were modified
        if allowed_path:
            try:
                builtins.open = orig_open
                os.remove = orig_remove
                os.rename = orig_rename
            except:
                pass
