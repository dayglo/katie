import os
import pandas as pd
import warnings

# Define mapping rules
mapping_rules = {
    # Add your mapping rules here
    # Example: "messy_value": "clean_value"
}


import re

# General purpose function to categorize body parts
def detect_body_part_category(value):
    # Define keywords for front, back, right, left, and body parts
    front_keywords = ["front"]
    back_keywords = ["back"]
    right_keywords = ["right"]
    left_keywords = ["left"]
    
    # Body parts
    body_part_keywords = [
        "paw", "thigh", "knee", "eye", "ear", "antler", "nose", "tail", "neck", "back", "mouth", "belly", "body", "throat"
    ]
    
    # Check for front/back
    position = "Unknown"
    if any(keyword in value.lower() for keyword in front_keywords):
        position = "Front"
    elif any(keyword in value.lower() for keyword in back_keywords):
        position = "Back"
    
    # Check for right/left
    side = "Unknown"
    if any(keyword in value.lower() for keyword in right_keywords):
        side = "Right"
    elif any(keyword in value.lower() for keyword in left_keywords):
        side = "Left"
    
    # Check for body part
    body_part = "Unknown"
    for keyword in body_part_keywords:
        if keyword in value.lower():
            body_part = keyword
            break
    
    return {
        "Original Value": value,
        "Position": position,
        "Side": side,
        "Body Part": body_part
    }

# Function to recombine the detected categories into clean values
def recombine_to_clean_value(value):
    categories = detect_body_part_category(value)
    
    position = categories["Position"]
    side = categories["Side"]
    body_part = categories["Body Part"]
    
    # Mapping rules to clean the recombined value
    recombined_value = ""
    
    # Add position for limbs or appendages
    if position != "Unknown":
        recombined_value += position.lower() + "_"
    
    # Add side (if applicable)
    if side != "Unknown":
        recombined_value += side.lower() + "_"
    
    # Add body part
    recombined_value += body_part
    
    # Final check if body part is "nose", we don't need any position or side
    if body_part == "nose":
        recombined_value = "nose"
    
    # If tail is involved, use "tail_end" or "tail_base" logic
    if body_part == "tail":
        if position == "Back":
            recombined_value = "tail_base"
        else:
            recombined_value = "tail_end"
    
    return recombined_value
def process_file(file_path, output_data):
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
                    clean_mark = recombine_to_clean_value(mark)
                    if (mark == 'eye' or mark == 'eye_n') and eye_side:
                        # print("    " + eye_side)
                        mark = eye_side

                    output_data.append({
                        'frame': int(row[frame_col]),
                        'stance': '',  # Stance is not provided in the input
                        'trial': trial_info,
                        'mark': recombine_to_clean_value(mark),
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
