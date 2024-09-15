import os
import pandas as pd
import warnings

# Function to map messy values to clean values
def map_to_clean_value(messy_value):
    return mapping_rules.get(messy_value, "Unknown")
    # Replace 'thai' with 'thigh'
    mark = mark.replace('thai', 'thigh')
    allowed_values = {
        "nose", "upper_jaw", "lower_jaw", "mouth_end_right", "mouth_end_left",
        "right_eye", "right_earbase", "right_earend", "right_antler_base", "right_antler_end",
        "left_eye", "left_earbase", "left_earend", "left_antler_base", "left_antler_end",
        "neck_base", "neck_end", "throat_base", "throat_end", "back_base", "back_end",
        "back_middle", "tail_base", "tail_end", "front_left_thai", "front_left_knee",
        "front_left_paw", "front_right_thai", "front_right_knee", "front_right_paw",
        "back_left_paw", "back_left_thai", "back_right_thai", "back_left_knee",
        "back_right_knee", "back_right_paw", "belly_bottom", "body_middle_right",
        "body_middle_left"
    }

    # If the mark is already clean, return it
    if mark in allowed_values:
        return mark

    # Normalize the mark by replacing spaces with underscores and splitting into words
    words = mark.replace(' ', '_').split('_')

    # Define possible components
    sides = {"left", "right"}
    positions = {"front", "back"}
    body_parts = {
        "nose", "jaw", "mouth", "eye", "earbase", "earend", "antler", "neck", "throat",
        "back", "tail", "thai", "knee", "paw", "belly", "body"
    }
    ends = {"end", "base", "middle", "bottom"}

    # Initialize components
    side = None
    position = None
    body_part = None
    end = None

    # Determine components
    for word in words:
        if word in sides:
            side = word
        elif word in positions:
            position = word
        elif word in body_parts:
            body_part = word
        elif word in ends:
            end = word

    # Construct the clean mark
    clean_mark = '_'.join(filter(None, [position, side, body_part, end]))

    # Handle special cases
    if body_part == "eye" and side:
        clean_mark = f"{side}_eye"
    elif body_part == "antler" and side and end:
        clean_mark = f"{side}_antler_{end}"
    elif body_part == "earbase" and side:
        clean_mark = f"{side}_earbase"
    elif body_part == "earend" and side:
        clean_mark = f"{side}_earend"

    # If the constructed mark is in allowed values, return it; otherwise, return the original mark
    if clean_mark in allowed_values:
        return clean_mark
    else:
        print(f"Warning: '{mark}' could not be mapped to a clean value. Returning original value.", UserWarning)
        return mark

def process_file(file_path, output_data):
    # Extract trial information from the file name
    file_name = os.path.basename(file_path)
    trial_info = file_name.split('_flattened.csv')[0]

    # Extract animal name from the directory structure
    animal_name = os.path.basename(os.path.dirname(file_path))

    # Extract video number from the trial information
    # Assuming the format is something like 'hyn_01_left', 'ott_02_right', etc.
    video_number = trial_info.split('_')[1].lstrip('0')  # Remove leading zeros

    # Construct the lookup file path
    lookupfile = f'./framelookup/{animal_name}/{video_number}.csv'

    # Read the CSV file
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        print(f"Skipping empty file: {file_path}")
        return

    # Extract body part names from the headers
    headers = df.columns
    body_parts = set(header.rsplit('_', 1)[0] for header in headers if '_x' in header)

    # Determine the eye side based on the trial name
    if trial_info.lower().endswith('_left'):
        eye_side = 'left_eye'
    elif trial_info.lower().endswith('_right'):
        eye_side = 'right_eye'
    else:
        eye_side = None

    for index, row in df.iterrows():
        # Iterate over each body part
        for body_part in body_parts:
            x_col = f'{body_part}_x'
            y_col = f'{body_part}_y'
            frame_col = f'{body_part}_frame'

            # Check if all necessary data is present and columns exist
            if x_col in row and y_col in row and frame_col in row:
                if pd.notna(row[x_col]) and pd.notna(row[y_col]) and pd.notna(row[frame_col]):
                    mark = body_part
                    # First, try the new mapping function
                    clean_mark = map_to_clean_value(mark)
                    if clean_mark == "Unknown":
                        # If the new mapping function returns "Unknown", use the existing function
                        clean_mark = map_body_part(mark)
                    if (mark == 'eye' or mark == 'eye_n') and eye_side:
                        # print("    " + eye_side)
                        mark = eye_side

                    output_data.append({
                        'frame': int(row[frame_col]),
                        'stance': '',  # Stance is not provided in the input
                        'trial': trial_info,
                        'mark': map_body_part(mark),
                        'x_t': row[x_col],
                        'y_t': row[y_col],
                        'animal': animal_name,  # Add the animal name to the output
                        'video_number': video_number,  # Add the video number to the output
                        'lookupfile': lookupfile  # Add the lookup file path to the output
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
