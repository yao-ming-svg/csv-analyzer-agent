"""
Simple Python-based file manager utilities.

Each operation is exposed as a dedicated function with clear
input and output parameters.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List


def list_files_in_folder(folder_path: str | os.PathLike) -> List[str]:
    """
    List all files (non-recursive) in the given folder.

    Args:
        folder_path: Path to the folder whose files should be listed.

    Returns:
        A list of file names (not full paths) contained in the folder.

    Raises:
        FileNotFoundError: If the folder does not exist.
        NotADirectoryError: If the provided path is not a directory.
        PermissionError: If the folder cannot be accessed.
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder}")

    return [entry.name for entry in folder.iterdir() if entry.is_file()]


def get_file_name(file_path: str | os.PathLike) -> str:
    """
    Get the name of a file from its path.

    Args:
        file_path: Full path to the file.

    Returns:
        The file name (including extension).

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")
    return path.name


def get_file_size(file_path: str | os.PathLike) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Full path to the file.

    Returns:
        File size in bytes.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")
    return path.stat().st_size


def rename_file(file_path: str | os.PathLike, new_name: str) -> Path:
    """
    Rename a file within its current directory.

    Args:
        file_path: Full path to the existing file.
        new_name: New file name (not a full path). Can include extension.

    Returns:
        Path object pointing to the renamed file.

    Raises:
        FileNotFoundError: If the file does not exist.
        FileExistsError: If a file with the new name already exists.
        PermissionError: If the operation is not permitted.
        ValueError: If new_name contains path separators.
    """
    if os.path.sep in new_name or (os.path.altsep and os.path.altsep in new_name):
        raise ValueError("new_name must be a name only, not a full path.")

    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"File does not exist: {src}")
    if not src.is_file():
        raise IsADirectoryError(f"Path is not a file: {src}")

    dest = src.with_name(new_name)

    if dest.exists():
        raise FileExistsError(f"Target file already exists: {dest}")

    src.rename(dest)
    return dest


def create_folder(folder_path: str | os.PathLike, exist_ok: bool = True) -> Path:
    """
    Create a new folder.

    Args:
        folder_path: Path of the folder to create.
        exist_ok: If True, do not raise an error if the folder already exists.

    Returns:
        Path object pointing to the created (or existing) folder.

    Raises:
        FileExistsError: If the folder exists and exist_ok is False.
        PermissionError: If the folder cannot be created.
    """
    path = Path(folder_path)

    if path.exists() and not path.is_dir():
        raise FileExistsError(f"Non-directory already exists at path: {path}")

    path.mkdir(parents=True, exist_ok=exist_ok)
    return path


def rename_folder(folder_path: str | os.PathLike, new_name: str) -> Path:
    """
    Rename a folder within its parent directory.

    Args:
        folder_path: Path to the existing folder.
        new_name: New folder name (not a full path).

    Returns:
        Path object pointing to the renamed folder.

    Raises:
        FileNotFoundError: If the folder does not exist.
        NotADirectoryError: If the path is not a folder.
        FileExistsError: If a folder with the new name already exists.
        PermissionError: If the operation is not permitted.
        ValueError: If new_name contains path separators.
    """
    if os.path.sep in new_name or (os.path.altsep and os.path.altsep in new_name):
        raise ValueError("new_name must be a name only, not a full path.")

    src = Path(folder_path)
    if not src.exists():
        raise FileNotFoundError(f"Folder does not exist: {src}")
    if not src.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {src}")

    dest = src.with_name(new_name)
    if dest.exists():
        raise FileExistsError(f"Target folder already exists: {dest}")

    src.rename(dest)
    return dest


def move_file(
    source_path: str | os.PathLike,
    destination_path: str | os.PathLike,
    overwrite: bool = False,
) -> Path:
    """
    Move a file from one path to another path.

    Args:
        source_path: Full path to the existing file.
        destination_path: Target path (can be a directory or full file path).
        overwrite: If True, overwrite an existing file at the destination.

    Returns:
        Path object pointing to the moved file at its new location.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IsADirectoryError: If source is a directory.
        FileExistsError: If destination exists and overwrite is False.
        PermissionError: If the operation is not permitted.
    """
    src = Path(source_path)
    dest = Path(destination_path)

    if not src.exists():
        raise FileNotFoundError(f"Source file does not exist: {src}")
    if not src.is_file():
        raise IsADirectoryError(f"Source path is not a file: {src}")

    # If destination is a directory, move the file into it keeping the same name.
    if dest.exists() and dest.is_dir():
        dest = dest / src.name

    if dest.exists():
        if not overwrite:
            raise FileExistsError(f"Destination file already exists: {dest}")
        # If overwriting, remove the existing file first to avoid issues on Windows.
        if dest.is_file():
            dest.unlink()

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return dest


__all__ = [
    "list_files_in_folder",
    "get_file_name",
    "get_file_size",
    "rename_file",
    "create_folder",
    "rename_folder",
    "move_file",
]


