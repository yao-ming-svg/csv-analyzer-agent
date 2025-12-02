# Example DSL script for the file manager

# Adjust the paths below to something that exists on your machine

# Ensure a working folder exists
CREATE_FOLDER "C:/tmp/dsl_demo"

# List files in the working folder
LIST_FILES "C:/tmp/dsl_demo"

# Move a file into the working folder
# MOVE_FILE "C:/path/to/some/file.txt" "C:/tmp/dsl_demo" OVERWRITE

# Once the file is there, you can inspect it (edit the name to match your file)
# GET_FILE_NAME "C:/tmp/dsl_demo/file.txt"
# GET_FILE_SIZE "C:/tmp/dsl_demo/file.txt"



