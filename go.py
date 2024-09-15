import os
import glob
import pandas as pd
from io import StringIO

# Function to handle debug printing
def debug_print(message):
    if os.getenv('DEBUG', '0') == '1':
        print(message)

def process_file(filepath):
    debug_print(f"Starting to process file: {filepath}")
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Remove the first line if it contains '#multi:'
    if lines[0].strip().startswith('#multi:'):
        debug_print("Removing '#multi:' line")
        debug_print("Removing empty line at the beginning")
        lines = lines[1:]

    # Remove empty lines at the beginning
    while lines and not lines[0].strip():
        lines = lines[1:]

    # Read header lines and remove the first element (t)
    header1 = lines[0].strip().split('\t')[1:]
    header2 = lines[1].strip().split('\t')[1:]

    debug_print(f"Header1: {header1}")
    debug_print(f"Header2: {header2}")

    # Read the data starting from the third line
    try:
        # Remove the first column (t) from each line before parsing
        expected_fields = len(header2)
        data_lines = []
        for i, line in enumerate(lines[2:], start=3):
            if line.strip():
                fields = line.split('\t')
                if len(fields) == expected_fields + 1:  # +1 because we removed the first column (t)
                    data_lines.append(fields[1])  # Append the line without the first column
                else:
                    debug_print(f"Skipping line {i} due to incorrect field count: {len(fields)}")
        debug_print("First few processed data lines after removing 't':")
        debug_print("First few processed data lines:")
        for line in data_lines[:5]:
            debug_print(line)

        data_str = ''.join(data_lines)
        # Use a flexible approach to handle varying numbers of fields
        data = pd.read_csv(StringIO(data_str), sep='\t', header=None, engine='python', names=range(len(header2)))
        debug_print("DataFrame after reading data:")
        debug_print(data.head())
    except pd.errors.ParserError as e:
        debug_print(f"Error parsing file {filepath}: {e}")
        for i, line in enumerate(lines[2:], start=3):
            fields = line.strip().split('\t')
            debug_print(f"Line {i}: {fields} (fields: {len(fields)})")
        raise

    debug_print("DataFrame after removing the first column (t):")
    debug_print(data.head())
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

    # Adjust the number of headers to match the data columns
    if len(combined_headers) > n:
        combined_headers = combined_headers[:n]
    elif len(combined_headers) < n:
        combined_headers += ['Unnamed'] * (n - len(combined_headers))

    debug_print("DataFrame with combined headers:")
    debug_print(data.head())
    data.columns = combined_headers

    # Add body part prefixes to x, y, and frame columns
    for i, body_part in enumerate(header1):
        if body_part:
            start_idx = i * 3
            end_idx = min(start_idx + 3, len(data.columns))
            for j in range(start_idx, end_idx):
                if data.columns[j].startswith(('x', 'y', 'frame')):
                    data.columns.values[j] = f"{body_part}_{data.columns[j]}"

    # Drop rows that are completely empty
    data = data.dropna(how='all')

    debug_print("Final DataFrame after dropping empty rows:")
    debug_print(data.head())

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
                print(f"Processing file: {os.path.basename(filepath)}")
                    df = process_file(filepath)
                    # Generate output filename
                    filename = os.path.basename(filepath).replace('.txt', '.csv')  # Save as CSV
                    output_filename = f"processed_{filename}"
                    output_filepath = os.path.join(animal_path, output_filename)

                    # Save the processed DataFrame to a new CSV file
                    df.to_csv(output_filepath, index=False)  # Default is comma-separated for CSV
                    debug_print(f"Processed {filename} and saved to {output_filename}")
                except Exception as e:
                    debug_print(f"Failed to process {filepath}: {e}")

if __name__ == "__main__":
    main()
