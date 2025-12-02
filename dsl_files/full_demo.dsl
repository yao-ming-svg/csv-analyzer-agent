# Example DSL script for the file manager

# Adjust the paths below to something that exists on your machine

# Ensure a working folder exists
CREATE_FOLDER "destination_folder"

# Move a file into the working folder
MOVE_FILE "origin_folder/document.txt" "destination_folder" OVERWRITE

# List files in the working folder (should now show document.txt)
LIST_FILES "destination_folder"

# Once the file is there, you can inspect it
GET_FILE_NAME "destination_folder/document.txt"
GET_FILE_SIZE "destination_folder/document.txt"