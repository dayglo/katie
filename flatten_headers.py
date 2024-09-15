import os
import pandas as pd

def flatten_headers(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Ensure there are enough lines to process headers
    if len(lines) < 3:
        print(f"File {file_path} does not have enough lines to process headers.")
        return
    header1 = lines[1].strip().split('\t')[1:]  # Skip the first column
    header2 = lines[2].strip().split('\t')[1:]  # Skip the first column

    # Create flattened headers
    flattened_headers = [
        f"{h1}_{h2}" for h1, h2 in zip(header1, header2)
    ]

    # Process the data lines
    data_lines = [line.strip().split('\t')[1:] for line in lines[3:]]

    # Write the processed data back to the file
    with open(file_path, 'w') as file:
        file.write('\t'.join(flattened_headers) + '\n')
        for data_line in data_lines:
            file.write('\t'.join(data_line) + '\n')

def process_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                flatten_headers(file_path)

if __name__ == "__main__":
    process_files('./files')
