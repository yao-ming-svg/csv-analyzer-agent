"""Run with an optional folder path:

    python test_file_manager.py <folder_path>

If no argument is provided, it will use the DEFAULT_TEST_FOLDER below.
"""

from __future__ import annotations

import sys
from pathlib import Path

from file_manager import (
    list_files_in_folder,
    get_file_name,
    get_file_size,
    rename_file,
    create_folder,
    rename_folder,
    move_file,
)

# Change this to any folder you want to use for testing
DEFAULT_TEST_FOLDER = Path("test_folder")


def main() -> None:
    # 0) Decide which folder to work with
    if len(sys.argv) > 1:
        base_folder = Path(sys.argv[1])
    else:
        base_folder = DEFAULT_TEST_FOLDER

    print(f"\nUsing test folder: {base_folder}\n")

    # 1) List all files in folder
    print("1) list_files_in_folder(base_folder)")
    try:
        files = list_files_in_folder(base_folder)
        print("   Result:", files)
    except Exception as e:
        print("   Error:", e)
        files = []

    # 2) Get file information - name
    if files:
        first_file = base_folder / files[0]
        print("\n2) get_file_name(first_file)")
        print("   first_file path:", first_file)
        try:
            name = get_file_name(first_file)
            print("   Result:", name)
        except Exception as e:
            print("   Error:", e)

        # 3) Get file information - size
        print("\n3) get_file_size(first_file)")
        try:
            size = get_file_size(first_file)
            print("   Result:", size, "bytes")
        except Exception as e:
            print("   Error:", e)
    else:
        print("\nNo files found in the folder; skipping name/size demos.")

    # 4) Rename a file (only if you have at least one file)
    if files:
        original_path = base_folder / files[0]
        print("\n4) rename_file(original_path, 'renamed_example.txt')")
        print("   original_path:", original_path)
        try:
            renamed_path = rename_file(original_path, "renamed_example.txt")
            print("   Renamed to:", renamed_path)
        except Exception as e:
            print("   Error:", e)
    else:
        print("\nNo file available to rename; skipping rename_file demo.")

    # 5) Create a new folder
    print("\n5) create_folder(base_folder / 'new_folder')")
    new_folder = base_folder / "new_folder"
    print("   new_folder path:", new_folder)
    try:
        created = create_folder(new_folder, exist_ok=True)
        print("   Result:", created)
    except Exception as e:
        print("   Error:", e)

    # 6) Rename a folder
    print("\n6) rename_folder(new_folder, 'renamed_folder')")
    try:
        renamed_folder = rename_folder(new_folder, "renamed_folder")
        print("   Renamed to:", renamed_folder)
    except Exception as e:
        print("   Error:", e)

    # 7) Move a file from one path to another path
    print("\n7) move_file(some_file, target_folder)")
    target_folder = base_folder / "target_folder"
    print("   target_folder path:", target_folder)
    try:
        create_folder(target_folder, exist_ok=True)
        # Try to move the renamed file if it exists
        candidate = base_folder / "renamed_example.txt"
        if not candidate.exists() and files:
            candidate = base_folder / files[0]

        if candidate.exists():
            print("   Source file:", candidate)
            moved = move_file(candidate, target_folder, overwrite=True)
            print("   Moved to:", moved)
        else:
            print("   No file found to move.")
    except Exception as e:
        print("   Error:", e)

    print("\nDone. Check the printed output and your filesystem to see the effects.")


if __name__ == "__main__":
    main()

