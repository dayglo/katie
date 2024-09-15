import os
import glob
import pandas as pd
from io import StringIO

def process_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Remove the first line if it contains '#multi:'
    if lines[0].strip().startswith('#multi:'):
        lines = lines[1:]
    
    # Remove empty lines at the beginning
    while lines and not lines[0].strip():
        lines = lines[1:]
    
    # Read header lines and remove the first element (t)
    header1 = lines[0].strip().split('\t')[1:]
    header2 = lines[1].strip().split('\t')[1:]
    
    # Read the data starting from the third line
    data_str = ''.join(lines[2:])
    data = pd.read_csv(StringIO(data_str), sep='\t', header=None, engine='python')
    
    # Remove the first column (t)
    data = data.iloc[:, 1:]
    
    # Ensure the headers match the number of data columns
    n = data.shape[1]
    header1 += [''] * (n - len(header1))
    header2 += [''] * (n - len(header2))
    
    # Combine the headers
    combined_headers = []
    for h1, h2 in zip(header1, header2):
        h1 = h1.strip()
        h2 = h2.strip()
        if h1 and h2:
            combined_header = f"{h1}_{h2}"
        elif h1:
            combined_header = h1
        elif h2:
            combined_header = h2
        else:
            combined_header = 'Unnamed'
        combined_headers.append(combined_header)
    
    # Assign the combined headers to the DataFrame
    data.columns = combined_headers
    
    # Drop rows that are completely empty
    data = data.dropna(how='all')
    
    return data

def main():
    # Define the base directory where the animal directories are located
    base_directory = './files'
    
    # Iterate over all subdirectories (animal types) in the base directory
    for animal_dir in os.listdir(base_directory):
        animal_path = os.path.join(base_directory, animal_dir)
        
        # Only proceed if it's a directory
        if os.path.isdir(animal_path):
            print(f"Processing animal type: {animal_dir}")
            
            # Define the file patterns to look for
            patterns = ['ott_*.txt', 'otter_*.txt']  # Adjust based on expected file patterns
            
            # Create a list of file paths matching the patterns in this animal's directory
            file_list = []
            for pattern in patterns:
                file_list.extend(glob.glob(os.path.join(animal_path, pattern)))
            
            # Process each file in the animal's directory
            for filepath in file_list:
                try:
                    df = process_file(filepath)
                    # Generate output filename
                    filename = os.path.basename(filepath).replace('.txt', '.csv')  # Save as CSV
                    output_filename = f"processed_{filename}"
                    output_filepath = os.path.join(animal_path, output_filename)
                    
                    # Save the processed DataFrame to a new CSV file
                    df.to_csv(output_filepath, index=False)  # Default is comma-separated for CSV
                    print(f"Processed {filename} and saved to {output_filename}")
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")

if __name__ == "__main__":
    main()
