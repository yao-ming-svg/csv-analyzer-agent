"""
Terminal-based file organizer that uses OpenAI to generate DSL code
for organizing files based on their type or content.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

# Try to load .env file using python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # If python-dotenv is not installed, manually load .env file
    def load_env_manually():
        """Manually load .env file if python-dotenv is not available."""
        env_file = Path(".env")
        if env_file.exists():
            try:
                # Use utf-8-sig to handle BOM (Byte Order Mark)
                with open(env_file, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            # Strip BOM and whitespace from key
                            key = key.strip().lstrip("\ufeff")
                            os.environ[key] = value.strip()
            except Exception:
                pass  # Silently fail if can't read .env file
    
    load_env_manually()

from file_manager import (
    list_files_in_folder,
    get_file_name,
    get_file_size,
)
from dsl_executor import DSLExecutor


def get_dsl_specification() -> str:
    """Returns the DSL specification documentation."""
    return """
The DSL is a line-oriented language for file management operations.

Lines:
    - Blank lines are ignored.
    - Lines starting with '#' are comments and ignored.

Syntax:
    COMMAND arg1 arg2 ...

Arguments:
    - Arguments are positional and depend on the command.
    - Use quotes if paths or names contain spaces.
    - Use forward slashes (/) for paths, even on Windows.
    - Paths are relative to the base folder being organized.

Available commands:

    CREATE_FOLDER <folder_path>
        Creates a new folder. If it already exists, no error is raised.
        Example: CREATE_FOLDER "images"

    MOVE_FILE <source_path> <destination_path> [OVERWRITE]
        Moves a file from source to destination.
        - source_path: relative path to the file (e.g., "document.txt")
        - destination_path: relative path to destination folder or file
        - OVERWRITE: optional flag to overwrite existing files
        Example: MOVE_FILE "photo.jpg" "images" OVERWRITE

    LIST_FILES <folder_path>
        Lists all files in a folder (for verification).
        Example: LIST_FILES "images"

Important notes:
    - All paths should be relative to the base folder being organized.
    - Use forward slashes (/) in paths, not backslashes.
    - Quote paths that contain spaces.
    - Organize files by creating folders based on file extensions or content types.
    - Use descriptive folder names like "images", "documents", "videos", "text_files", etc.
"""


def analyze_folder(base_folder: str) -> Dict:
    """
    Analyzes a folder and returns detailed information about all files.

    Args:
        base_folder: Path to the folder to analyze.

    Returns:
        Dictionary containing folder path and list of file information.
    """
    base_path = Path(base_folder).resolve()

    if not base_path.exists():
        raise FileNotFoundError(f"Folder does not exist: {base_path}")
    if not base_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {base_path}")

    files = list_files_in_folder(base_folder)
    file_details = []

    for file_name in files:
        file_path = base_path / file_name
        try:
            size = get_file_size(str(file_path))
            file_info = {
                "name": file_name,
                "size_bytes": size,
                "extension": file_path.suffix.lower(),
            }
            file_details.append(file_info)
        except Exception as e:
            # If we can't get file info, still include the name
            file_info = {
                "name": file_name,
                "size_bytes": None,
                "extension": file_path.suffix.lower(),
                "error": str(e),
            }
            file_details.append(file_info)

    return {
        "folder_path": str(base_path),
        "folder_name": base_path.name,
        "file_count": len(file_details),
        "files": file_details,
    }


def generate_summary(analysis: Dict) -> str:
    """
    Generates a human-readable summary of the folder analysis.

    Args:
        analysis: Dictionary returned from analyze_folder().

    Returns:
        Formatted string summary.
    """
    summary = f"""
=== Folder Analysis Summary ===

Base Folder: {analysis['folder_path']}
Folder Name: {analysis['folder_name']}
Total Files: {analysis['file_count']}

Files:
"""
    for file_info in analysis["files"]:
        name = file_info["name"]
        size = file_info.get("size_bytes")
        ext = file_info.get("extension", "")
        
        if size is not None:
            size_str = f"{size:,} bytes"
            if size > 1024 * 1024:
                size_str += f" ({size / (1024 * 1024):.2f} MB)"
            elif size > 1024:
                size_str += f" ({size / 1024:.2f} KB)"
        else:
            size_str = "unknown size"
        
        summary += f"  - {name} ({size_str}) [Extension: {ext or 'none'}]\n"

    # Group by extension for overview
    ext_counts: Dict[str, int] = {}
    for file_info in analysis["files"]:
        ext = file_info.get("extension", "").lower() or "no_extension"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    summary += "\nFile Types (by extension):\n"
    for ext, count in sorted(ext_counts.items()):
        ext_display = ext if ext else "(no extension)"
        summary += f"  - {ext_display}: {count} file(s)\n"

    return summary


def call_openai_api(api_key: str, folder_analysis: Dict, dsl_spec: str) -> str:
    """
    Calls OpenAI API to generate DSL code for organizing files.

    Args:
        api_key: OpenAI API key.
        folder_analysis: Dictionary from analyze_folder().
        dsl_spec: DSL specification documentation.

    Returns:
        Generated DSL code as a string.
    """
    try:
        import openai
    except ImportError:
        raise ImportError(
            "The 'openai' package is required. Install it with: pip install openai"
        )

    client = openai.OpenAI(api_key=api_key)

    # Build the prompt
    files_info = "\n".join([
        f"- {f['name']} ({f.get('size_bytes', 'unknown')} bytes, extension: {f.get('extension', 'none')})"
        for f in folder_analysis["files"]
    ])

    prompt = f"""You are a file organization assistant. Given a list of files in a folder, generate DSL code to organize them into subfolders based on their file types or content.

Base folder path: {folder_analysis['folder_path']}
Base folder name: {folder_analysis['folder_name']}
Number of files: {folder_analysis['file_count']}

Files in the folder:
{files_info}

DSL Specification:
{dsl_spec}

Instructions:
1. Analyze the files and group them by file extension or content type (e.g., images, documents, videos, text files, etc.)
2. Create appropriate subfolders for each category
3. Move files into their corresponding folders using MOVE_FILE commands
4. Use relative paths (relative to the base folder: "{folder_analysis['folder_name']}")
5. Use forward slashes (/) in all paths
6. Include OVERWRITE flag when moving files to avoid errors
7. Add comments to explain the organization strategy
8. Only output valid DSL code, no explanations or markdown formatting

Generate the DSL code now:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates DSL code for file organization. Only output valid DSL code without markdown formatting or explanations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        dsl_code = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if dsl_code.startswith("```"):
            lines = dsl_code.split("\n")
            # Remove first line (```dsl or ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            dsl_code = "\n".join(lines)

        return dsl_code

    except Exception as e:
        raise RuntimeError(f"Error calling OpenAI API: {e}")


def main() -> None:
    """Main program entry point."""
    print("=" * 60)
    print("File Organizer - AI-Powered File Organization")
    print("=" * 60)
    print()

    # Step 1: Get base folder from user
    base_folder = input("Enter the base folder path to organize: ").strip()
    if not base_folder:
        print("Error: Folder path cannot be empty.")
        return

    # Resolve the path
    base_path = Path(base_folder).resolve()
    if not base_path.exists():
        print(f"Error: Folder does not exist: {base_path}")
        return
    if not base_path.is_dir():
        print(f"Error: Path is not a directory: {base_path}")
        return

    print(f"\nAnalyzing folder: {base_path}")
    print("-" * 60)

    # Step 2: Analyze folder and generate summary
    try:
        analysis = analyze_folder(str(base_path))
        summary = generate_summary(analysis)
        print(summary)
        print("-" * 60)
    except Exception as e:
        print(f"Error analyzing folder: {e}")
        return

    if analysis["file_count"] == 0:
        print("No files found in the folder. Nothing to organize.")
        return

    # Confirm before proceeding
    print()
    response = input("Proceed with AI-generated organization? (yes/no): ").strip().lower()
    if response not in ("yes", "y"):
        print("Organization cancelled.")
        return

    # Step 3: Call OpenAI API
    # Try to load from .env file again (in case it wasn't loaded at startup)
    env_file = Path(".env")
    if env_file.exists() and not os.getenv("OPENAI_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Manual load
            try:
                # Use utf-8-sig to handle BOM (Byte Order Mark)
                with open(env_file, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            # Strip BOM and whitespace from key
                            key = key.strip().lstrip("\ufeff")
                            if key == "OPENAI_API_KEY":
                                os.environ["OPENAI_API_KEY"] = value.strip()
                                break
            except Exception:
                pass
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nError: OPENAI_API_KEY not found.")
        print("Please ensure the .env file exists with: OPENAI_API_KEY=your_key_here")
        print("Or set it as an environment variable.")
        return

    print("\nCalling OpenAI API to generate organization DSL code...")
    try:
        dsl_spec = get_dsl_specification()
        dsl_code = call_openai_api(api_key, analysis, dsl_spec)
        print("\nGenerated DSL code:")
        print("=" * 60)
        print(dsl_code)
        print("=" * 60)
    except Exception as e:
        print(f"Error generating DSL code: {e}")
        return

    # Step 4: Confirm execution
    print()
    response = input("Execute the generated DSL code? (yes/no): ").strip().lower()
    if response not in ("yes", "y"):
        print("Execution cancelled.")
        return

    # Step 5: Execute DSL code
    print("\nExecuting DSL code...")
    print("-" * 60)

    # Change to the base folder directory so relative paths work correctly
    original_cwd = os.getcwd()
    try:
        os.chdir(str(base_path))
        executor = DSLExecutor(echo=True)
        results = executor.run_script_text(dsl_code)

        # Check for errors
        errors = [r for r in results if not r.success]
        if errors:
            print("\n" + "=" * 60)
            print("WARNING: Some commands had errors:")
            for result in errors:
                print(f"  Line {result.line_number}: {result.error}")
        else:
            print("\n" + "=" * 60)
            print("✓ All commands executed successfully!")

        # Show final state
        print("\nFinal folder state:")
        print("-" * 60)
        final_analysis = analyze_folder(".")
        final_summary = generate_summary(final_analysis)
        print(final_summary)

    except Exception as e:
        print(f"Error executing DSL code: {e}")
    finally:
        os.chdir(original_cwd)

    print("\n" + "=" * 60)
    print("File organization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

