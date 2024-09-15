import csv
import sys

def read_frame_lookup(file_path):
    data = {}

    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        
        # Skip the first header row
        next(reader)
        
        # Read the second header row for body parts
        body_parts = next(reader)[1:]  # Skip the first column
        
        # Read the third header row for coordinates
        coords = next(reader)[1:]  # Skip the first column
        
        # Process each row in the CSV
        for row in reader:
            frame = int(row[0])
            data[frame] = {}
            
            # Iterate over body parts and their corresponding x, y, likelihood
            for i in range(0, len(body_parts), 3):
                body_part = body_parts[i]
                x = float(row[i + 1])
                y = float(row[i + 2])
                # likelihood = float(row[i + 3])  # If you need likelihood, you can include it
                
                data[frame][body_part] = (x, y)
    
    return data

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python frame_lookup.py <filename> <frame> <body_part>")
        sys.exit(1)

    filename = sys.argv[1]
    frame = int(sys.argv[2])
    body_part = sys.argv[3]

    frame_data = read_frame_lookup(filename)

    if frame in frame_data and body_part in frame_data[frame]:
        x, y = frame_data[frame][body_part]
        print(f"Frame {frame}, Body Part '{body_part}': x = {x}, y = {y}")
    else:
        print(f"Data not found for Frame {frame}, Body Part '{body_part}'.")
