import csv
from frame_lookup import read_frame_lookup

def process_output_csv(input_csv, output_csv):
    with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['new_x', 'new_y']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            frame = int(row['frame'])
            body_part = row['mark']
            lookup_file = row['lookupfile']

            # Read the frame lookup data
            frame_data = read_frame_lookup(lookup_file)

            # Get the new x and y values
            if frame in frame_data and body_part in frame_data[frame]:
                new_x, new_y = frame_data[frame][body_part]
            else:
                new_x, new_y = None, None

            # Add new x and y to the row
            row['new_x'] = new_x
            row['new_y'] = new_y

            # Write the updated row to the output file
            writer.writerow(row)

if __name__ == "__main__":
    input_csv = 'output.csv'
    output_csv = 'output2.csv'
    process_output_csv(input_csv, output_csv)
