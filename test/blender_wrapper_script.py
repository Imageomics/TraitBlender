
#! /usr/bin/python3
import sys
import subprocess

# Get the JSON file path from the command-line arguments
json_file_path = sys.argv[1] if len(sys.argv) > 1 else None

if json_file_path:
    blender_command = [
        "C://Program Files/Blender Foundation/Blender 3.3/blender.exe",
        "--background",
        "--python",
        "read_json_variables.py"
    ]
    # Execute Blender with the appropriate Python script and arguments
    subprocess.run(blender_command)
else:
    print("Please provide the path to the JSON file as an argument.")
