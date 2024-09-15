import os
import pandas as pd

def process_file(file_path, output_data):
    # Extract trial information from the file name
    file_name = os.path.basename(file_path)
    trial_info = file_name.split('_flattened.csv')[0]

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Extract body part names from the headers
    headers = df.columns
    body_parts = [header.rsplit('_', 1)[0] for header in headers if '_x' in header]

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate over each body part
        for body_part in body_parts:
            x_col = f'{body_part}_x'
            y_col = f'{body_part}_y'
            frame_col = f'{body_part}_frame'

            if pd.notna(row[x_col]) and pd.notna(row[y_col]):
                output_data.append({
                    'frame': int(row[frame_col]),
                    'stance': '',  # Stance is not provided in the input
                    'trial': trial_info,
                    'mark': body_part,
                    'x_t': row[x_col],
                    'y_t': row[y_col]
                })

def process_all_files(base_dir, output_file):
    output_data = []

    # Walk through the directory and process each CSV file
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('_flattened.csv'):
                file_path = os.path.join(root, file)
                process_file(file_path, output_data)

    # Create a DataFrame from the output data
    output_df = pd.DataFrame(output_data)

    # Save the output DataFrame to a CSV file
    output_df.to_csv(output_file, index=False)

# Define the base directory and output file
base_dir = './files'
output_file = 'output.csv'

# Process all files and generate the output
process_all_files(base_dir, output_file)
