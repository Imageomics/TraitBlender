#!/bin/bash

# Path to Blender executable
# blender_executable="C:/Program Files/Blender Foundation/Blender 3.3/blender.exe"

# Path to the bpy script
script_path="generate_dataset.py"  # Replace with the actual path to your updated script

# Paths to the make_mesh_function, csv_file, and json_file
make_mesh_function_path="make_contreras_snail.py"
csv_file_path="contreras_sample.csv"
json_file_path="traitblender_settings.json"
images_per_individual="1,5,17"
individual_indices="0,10,8:11"

# Run Blender with the bpy script and the paths as arguments
singularity run docker://ghcr.io/imageomics/traitblender:1.0.0 blender --background --python "$script_path" -- "$make_mesh_function_path" "$csv_file_path" "$json_file_path" "$images_per_individual" "$individual_indices"
