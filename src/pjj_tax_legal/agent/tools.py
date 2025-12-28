"""
Simplified memory tools - same functionality, minimal complexity.

This module provides thin wrappers around Python built-ins for LLM-generated code.
Functions are kept simple to reduce complexity while maintaining identical behavior.

All functions must have:
- Same names (LLM expects these)
- Same signatures (agent.py passes these parameters)
- Same return types (code depends on these)
"""

import os


def get_size(file_or_dir_path: str) -> int:
    """
    Get the size of a file or directory in bytes.

    Args:
        file_or_dir_path: Path to file/dir, or empty string for total memory size

    Returns:
        Size in bytes
    """
    if not file_or_dir_path or file_or_dir_path == "":
        # Total memory directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(os.getcwd()):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size

    # Specific file or directory
    if os.path.isfile(file_or_dir_path):
        return os.path.getsize(file_or_dir_path)
    elif os.path.isdir(file_or_dir_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(file_or_dir_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size
    else:
        raise FileNotFoundError(f"Path not found: {file_or_dir_path}")


def create_file(file_path: str, content: str = "") -> bool:
    """
    Create a new file with content, auto-creating parent directories.

    Args:
        file_path: Path to file to create
        content: Content to write (default: empty)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directories
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def _create_dir(dir_path: str) -> bool:
    """
    DISABLED: Create a new directory.

    This function has been disabled (renamed with underscore prefix) to prevent
    the Agent from creating unwanted directories during search operations.
    Agents should only READ files, not create directories.

    Args:
        dir_path: Path to directory

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception:
        return False


def update_file(file_path: str, old_content: str, new_content: str) -> bool:
    """
    Find and replace content in a file.

    Args:
        file_path: Path to file to update
        old_content: Content to find
        new_content: Content to replace with

    Returns:
        True if successful, False if old_content not found or other error
    """
    try:
        # Check file exists
        if not os.path.isfile(file_path):
            return False

        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        # Check old_content exists
        if old_content not in current_content:
            return False

        # Replace (first occurrence only)
        updated_content = current_content.replace(old_content, new_content, 1)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return True
    except Exception:
        return False


def read_file(file_path: str) -> str:
    """
    Read a file's content.

    Args:
        file_path: Path to file to read

    Returns:
        File content, or error message string if fails
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist"

        if not os.path.isfile(file_path):
            return f"Error: {file_path} is not a file"

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        return f"Error: Permission denied accessing {file_path}"
    except Exception as e:
        return f"Error: {e}"


def list_files() -> str:
    """
    List files and directories in current working directory.

    Returns:
        String listing of directory contents, or error message
    """
    try:
        cwd = os.getcwd()
        items = sorted(os.listdir(cwd))
        # Filter out hidden files and pycache
        items = [item for item in items if not item.startswith(".") and item != "__pycache__"]
        return "\n".join(items) if items else "(empty)"
    except Exception as e:
        return f"Error: {e}"


def delete_file(file_path: str) -> bool:
    """
    Delete a file.

    Args:
        file_path: Path to file to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        os.remove(file_path)
        return True
    except Exception:
        return False


def go_to_link(link_string: str) -> str:
    """
    Read a file referenced by a link.

    Args:
        link_string: Link in format "path/to/file" or "[[path/to/file]]"

    Returns:
        File content, or error message if fails
    """
    try:
        # Handle Obsidian-style [[links]]
        if link_string.startswith("[[") and link_string.endswith("]]"):
            file_path = link_string[2:-2]  # Remove [[ and ]]
            if not file_path.endswith(".md"):
                file_path += ".md"
        else:
            file_path = link_string

        # Check file exists
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"

        if not os.path.isfile(file_path):
            return f"Error: {file_path} is not a file"

        # Read and return
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


def check_if_file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to check

    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(file_path)


def check_if_dir_exists(dir_path: str) -> bool:
    """
    Check if a directory exists.

    Args:
        dir_path: Path to check

    Returns:
        True if directory exists, False otherwise
    """
    return os.path.isdir(dir_path)
