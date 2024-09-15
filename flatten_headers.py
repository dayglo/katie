import os
import pandas as pd

def flatten_headers(file_path):
    # Read the file, skipping the first line and using the first two rows as headers
    df = pd.read_csv(file_path, sep='\t', skiprows=1, header=[0, 1])
    
    # Flatten the multi-level column headers
    df.columns = ['_'.join(filter(None, col)).strip() for col in df.columns]
    
    # Drop the first column (t)
    df.drop(columns=df.columns[0], inplace=True)
    
    # Write the modified DataFrame back to the file
    df.to_csv(file_path, sep='\t', index=False)

def process_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                flatten_headers(file_path)

if __name__ == "__main__":
    process_files('./files')
