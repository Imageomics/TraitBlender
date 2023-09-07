
import json
import sys

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to the JSON file as an argument.")
    else:
        json_file_path = sys.argv[1]
        json_data = read_json_file(json_file_path)

        for key, value in json_data.items():
            print(f"{key}: {value}")

