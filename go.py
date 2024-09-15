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
    
    # Split the data into lines and process each line
    data_lines = data_str.splitlines()
    valid_data = []
    for line in data_lines:
        try:
            # Attempt to parse the line
            parsed_line = pd.read_csv(StringIO(line), sep='\t', header=None, engine='python')
            valid_data.append(parsed_line)
        except Exception as e:
            # Print the line and the error if parsing fails
            print(f"Bad line: {line} - Error: {e}")
    
    # Concatenate all valid data into a single DataFrame
    if valid_data:
        data = pd.concat(valid_data, ignore_index=True)
    else:
        data = pd.DataFrame()
    
    # Remove the first column (t)
    data = data.iloc[:, 1:]
    
    # Ensure the headers match the number of data columns
    n = data.shape[1]
    header1 += [''] * (n - len(header1))
    header2 += [''] * (n - len(header2))
    
    # Combine the headers with the desired format
    combined_headers = []
    for i in range(len(header1)):
        part_name = header1[i].strip() if header1[i].strip() else 'Unnamed'
        suffix = header2[i].strip() if header2[i].strip() else 'Unnamed'
        combined_headers.append(f"{part_name}_{suffix}")
    
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
        if os.path.isdir(animal_path) and not animal_dir.startswith('.'):
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
