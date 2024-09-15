import os
import csv

def flatten_headers(file_path, output_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        lines = list(reader)

    # Ensure there are at least three lines for headers
    if len(lines) < 3:
        print(f"File {file_path} does not have enough header lines.")
        return

    header_line1 = lines[0]  # #multi:
    header_line2 = lines[1]
    header_line3 = lines[2]

    # Initialize variables
    body_part_name = ''
    new_header = []
    skip_columns = []

    # Process headers to flatten them
    for i in range(len(header_line3)):
        var_name = header_line3[i].strip()
        part_name = header_line2[i].strip() if i < len(header_line2) else ''

        if var_name == 't':
            new_header.append('t')
            skip_columns.append(False)
            continue

        if part_name:
            body_part_name = part_name

        if var_name:
            column_name = f"{body_part_name}_{var_name}"
            new_header.append(column_name)
            skip_columns.append(False)
        else:
            # Skip columns where variable name is empty
            skip_columns.append(True)

    # Process data rows
    data_rows = []
    for row in lines[3:]:
        # Extend row to match header length if necessary
        while len(row) < len(new_header):
            row.append('')

        # Ensure skip_columns matches the length of the row
        if len(skip_columns) < len(row):
            skip_columns.extend([True] * (len(row) - len(skip_columns)))

        new_row = []        
        for i, cell in enumerate(row):
            if not skip_columns[i]:
                new_row.append(cell.strip() if cell.strip() else '')
        data_rows.append(new_row)

    # Write output to new file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(new_header)
        writer.writerows(data_rows)

def process_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt'):
                input_file = os.path.join(root, file)
                # Modify the output path as needed; here we append '_flattened' to the filename
                output_file = os.path.join(root, file.replace('.txt', '_flattened.txt'))
                flatten_headers(input_file, output_file)
                print(f"Processed {input_file} -> {output_file}")

# Example usage:
process_files('./files')
