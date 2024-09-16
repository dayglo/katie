import csv
from frame_lookup import read_frame_lookup
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def process_output_csv(input_csv, output_csv):
    print(f"{Fore.GREEN}Processing input CSV: {input_csv}{Style.RESET_ALL}")
    # Dictionary to cache frame data for each lookup file
    lookup_cache = {}

    with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['new_x', 'new_y']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            frame = int(row['frame'])
            body_part = row['mark']
            lookup_file = row['lookupfile']

            # Check if the lookup file data is already cached
            if lookup_file not in lookup_cache:
                # Read the frame lookup data and cache it
                lookup_cache[lookup_file] = read_frame_lookup(lookup_file)

            # Get the frame data from the cache
            frame_data = lookup_cache[lookup_file]

            # Get the new x and y values
            if frame in frame_data and body_part in frame_data[frame]:
                new_x, new_y = frame_data[frame][body_part]
                print(f"{Fore.CYAN}Frame {frame}, Body Part '{body_part}': new_x = {new_x}, new_y = {new_y} from {lookup_file}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Data not found for Frame {frame}, Body Part '{body_part}' in {lookup_file}.{Style.RESET_ALL}")
                new_x, new_y = None, None

            # Add new x and y to the row
            row['new_x'] = new_x
            row['new_y'] = new_y

            # Write the updated row to the output file
            writer.writerow(row)
            print(f"{Fore.YELLOW}Written to output CSV: {output_csv}{Style.RESET_ALL}")

if __name__ == "__main__":
    input_csv = 'output.csv'
    output_csv = 'output2.csv'
    process_output_csv(input_csv, output_csv)
