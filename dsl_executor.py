"""
Simple domain-specific language (DSL) executor for the file_manager utilities.

The DSL is a line-oriented language. Each non-empty, non-comment line
contains exactly one command that maps directly to one of the functions in
`file_manager.py`.

Lines:
    - Blank lines are ignored.
    - Lines starting with '#' are comments and ignored.

Syntax:
    COMMAND arg1 arg2 ...

Arguments:
    - Arguments are positional and depend on the command.
    - Use quotes if paths or names contain spaces.
    - Windows paths should be quoted to avoid issues with backslashes.
    - Parsing uses Python's shlex.split, so quoting/escaping follows shell
      conventions (e.g., "C:\\My Folder\\file.txt").

Available commands (and their mapping to file_manager functions):

    LIST_FILES <folder_path>
        -> list_files_in_folder(folder_path)
        Prints list of file names.

    GET_FILE_NAME <file_path>
        -> get_file_name(file_path)
        Prints file name.

    GET_FILE_SIZE <file_path>
        -> get_file_size(file_path)
        Prints size in bytes.

    RENAME_FILE <file_path> <new_name>
        -> rename_file(file_path, new_name)
        Prints new path.

    CREATE_FOLDER <folder_path>
        -> create_folder(folder_path)
        Prints folder path (created or existing).

    RENAME_FOLDER <folder_path> <new_name>
        -> rename_folder(folder_path, new_name)
        Prints new path.

    MOVE_FILE <source_path> <destination_path> [OVERWRITE]
        -> move_file(source_path, destination_path, overwrite=bool)
        If the optional third token is the literal OVERWRITE, existing files
        at the destination will be overwritten.
        Prints new path.

Example script:

    # Create a folder and move a file
    CREATE_FOLDER "C:/tmp/my_folder"
    LIST_FILES "C:/tmp"
    MOVE_FILE "C:/tmp/source.txt" "C:/tmp/my_folder" OVERWRITE
    GET_FILE_SIZE "C:/tmp/my_folder/source.txt"
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from file_manager import (
    list_files_in_folder,
    get_file_name,
    get_file_size,
    rename_file,
    create_folder,
    rename_folder,
    move_file,
)


@dataclass
class ExecutionResult:
    """Holds the outcome of executing a single DSL line."""

    line_number: int
    line: str
    command: Optional[str]
    success: bool
    result: Optional[object] = None
    error: Optional[Exception] = None


class DSLExecutor:
    """
    Executor for the simple file-manager DSL.

    Usage:
        executor = DSLExecutor()
        results = executor.run_script_text(script_text)
        for res in results:
            print(res)
    """

    def __init__(self, echo: bool = True) -> None:
        """
        Args:
            echo: If True, print results and errors as commands execute.
        """
        self.echo = echo
        self._command_table: dict[str, Callable[[List[str]], object]] = {
            "LIST_FILES": self._cmd_list_files,
            "GET_FILE_NAME": self._cmd_get_file_name,
            "GET_FILE_SIZE": self._cmd_get_file_size,
            "RENAME_FILE": self._cmd_rename_file,
            "CREATE_FOLDER": self._cmd_create_folder,
            "RENAME_FOLDER": self._cmd_rename_folder,
            "MOVE_FILE": self._cmd_move_file,
        }

    # Public API -----------------------------------------------------

    def run_script_text(self, script: str) -> List[ExecutionResult]:
        """
        Execute DSL commands from a string containing the script.

        Args:
            script: Entire DSL script as a string.

        Returns:
            List of ExecutionResult, one for each non-empty, non-comment line.
        """
        results: List[ExecutionResult] = []
        for index, raw_line in enumerate(script.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                # Skip blank lines and comments
                continue

            try:
                tokens = shlex.split(line)
            except ValueError as e:
                result = ExecutionResult(
                    line_number=index,
                    line=raw_line,
                    command=None,
                    success=False,
                    result=None,
                    error=e,
                )
                results.append(result)
                if self.echo:
                    print(f"[Line {index}] Parse error: {e}")
                continue

            if not tokens:
                continue

            command = tokens[0].upper()
            args = tokens[1:]

            handler = self._command_table.get(command)
            if handler is None:
                err = ValueError(f"Unknown command: {command}")
                result = ExecutionResult(
                    line_number=index,
                    line=raw_line,
                    command=command,
                    success=False,
                    result=None,
                    error=err,
                )
                results.append(result)
                if self.echo:
                    print(f"[Line {index}] {err}")
                continue

            try:
                value = handler(args)
                result = ExecutionResult(
                    line_number=index,
                    line=raw_line,
                    command=command,
                    success=True,
                    result=value,
                    error=None,
                )
                results.append(result)
                if self.echo:
                    print(f"[Line {index}] {command} -> {value}")
            except Exception as e:  # noqa: BLE001 - want to surface any error
                result = ExecutionResult(
                    line_number=index,
                    line=raw_line,
                    command=command,
                    success=False,
                    result=None,
                    error=e,
                )
                results.append(result)
                if self.echo:
                    print(f"[Line {index}] {command} ERROR: {e}")

        return results

    def run_script_file(self, script_path: str | Path) -> List[ExecutionResult]:
        """
        Execute DSL commands from a file.

        Args:
            script_path: Path to the script file to execute.

        Returns:
            List of ExecutionResult for each executed line.

        Notes:
            All relative paths used inside the DSL script are interpreted
            relative to the folder that contains the script file (not the
            process's current working directory).
        """
        path = Path(script_path).resolve()
        text = path.read_text(encoding="utf-8")

        original_cwd = os.getcwd()
        try:
            # Make all relative paths inside the script resolve from the
            # script's directory for a more intuitive authoring experience.
            os.chdir(str(path.parent))
            return self.run_script_text(text)
        finally:
            os.chdir(original_cwd)

    # Command handlers -----------------------------------------------

    def _require_args(self, args: List[str], expected: int, name: str) -> None:
        if len(args) != expected:
            raise ValueError(f"{name} expects {expected} argument(s), got {len(args)}")

    def _cmd_list_files(self, args: List[str]) -> str:
        self._require_args(args, 1, "LIST_FILES")
        folder_path = args[0]
        folder = Path(folder_path).resolve()
        files = list_files_in_folder(folder_path)
        return f"Folder: {folder}\nFiles: {files}"

    def _cmd_get_file_name(self, args: List[str]) -> str:
        self._require_args(args, 1, "GET_FILE_NAME")
        file_path = args[0]
        return get_file_name(file_path)

    def _cmd_get_file_size(self, args: List[str]) -> int:
        self._require_args(args, 1, "GET_FILE_SIZE")
        file_path = args[0]
        return get_file_size(file_path)

    def _cmd_rename_file(self, args: List[str]):
        self._require_args(args, 2, "RENAME_FILE")
        file_path, new_name = args
        return rename_file(file_path, new_name)

    def _cmd_create_folder(self, args: List[str]):
        self._require_args(args, 1, "CREATE_FOLDER")
        folder_path = args[0]
        return create_folder(folder_path, exist_ok=True)

    def _cmd_rename_folder(self, args: List[str]):
        self._require_args(args, 2, "RENAME_FOLDER")
        folder_path, new_name = args
        return rename_folder(folder_path, new_name)

    def _cmd_move_file(self, args: List[str]):
        if len(args) not in (2, 3):
            raise ValueError(
                "MOVE_FILE expects 2 or 3 arguments: "
                "<source_path> <destination_path> [OVERWRITE]"
            )
        source_path = args[0]
        destination_path = args[1]
        overwrite = False
        if len(args) == 3:
            flag = args[2].upper()
            if flag == "OVERWRITE":
                overwrite = True
            else:
                raise ValueError(
                    "MOVE_FILE third argument must be OVERWRITE if provided."
                )
        return move_file(source_path, destination_path, overwrite=overwrite)


def main() -> None:
    """
    Small CLI helper so you can run a DSL script directly:

        python dsl_executor.py path/to/script.dsl
    """

    import sys

    if len(sys.argv) != 2:
        print("Usage: python dsl_executor.py <script_file>")
        raise SystemExit(1)

    script_file = sys.argv[1]
    executor = DSLExecutor(echo=True)
    executor.run_script_file(script_file)


if __name__ == "__main__":
    main()


