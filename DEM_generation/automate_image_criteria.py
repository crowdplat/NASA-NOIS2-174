import numpy as np
import pandas as pd
import re

# stereo image criteria automation 

def px(sc_az_gnd, emi):
    
    return -np.tan(emi)*np.cos(sc_az_gnd)
    

def py(sc_az_gnd, emi):
    
    return np.tan(emi)*np.sin(sc_az_gnd)

def calcualte_dp(sc_az_gnd_1, emi_1, sc_az_gnd_2, emi_2):
    # Strength of Stereo
    
    px_1 = px(sc_az_gnd_1, emi_1)
    px_2 = px(sc_az_gnd_2, emi_2)    
    py_1 = py(sc_az_gnd_1, emi_1)
    py_2 = py(sc_az_gnd_2, emi_2)
    
    dp = np.sqrt((px_1 - px_2)**2 + (py_1 - py_2)**2) 
    
    return dp

def calcualte_dsh(sun_az_gnd_1, inc_1, sun_az_gnd_2, inc_2):
    # Illumination Compatibility
    
    shx_1 = px(sun_az_gnd_1, inc_1)
    shx_2 = px(sun_az_gnd_2, inc_2)    
    shy_1 = py(sun_az_gnd_1, inc_1)
    shy_2 = py(sun_az_gnd_2, inc_2)
    
    dsh = np.sqrt((shx_1 - shx_2)**2 + (shy_1 - shy_2)**2) 
    
    return dsh

def image_coord_for_campt(file_name):
    
    import pdr
    import re
    
    header = pdr.read(f"Thomas_practice/{file_name}.cub")["LABEL"]
    # Extract top-left and bottom-right coordinates
    
    # Regular expressions to match "Samples" and "Lines"
    samples_regex = r"\s+Samples\s*=\s*(\d+)\n" # columns
    lines_regex = r"\s+Lines\s*=\s*(\d+)\n" # rows

    # Extracting the values using the regex
    samples = int(re.search(samples_regex, header).group(1))
    lines = int(re.search(lines_regex, header).group(1))

    top_left = 1, 1
    bottom_right = lines, samples
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Calculate the other two corners
    top_right = (x1, y2)
    bottom_left = (x2, y1)

    # Calculate the midpoints
    midpoint_top = (x1, (y1 + y2) // 2)
    midpoint_bottom = (x2, (y1 + y2) // 2)
    midpoint_left = ((x1 + x2) // 2, y1)
    midpoint_right = ((x1 + x2) // 2, y2)
    midpoint = ((x1 + x2) // 2,(y1 + y2) // 2)
    
    # 9 coordinates
    coordinates = [top_left, top_right, bottom_left, bottom_right, midpoint_top, midpoint_bottom, midpoint_left, midpoint_right, midpoint]
    
    # print(len(coordinates))
    
    # Save to a text file with no parentheses
    file_path = f'{file_name}_image_coordinates.txt'
    with open(file_path, 'w') as file:
        for coord in coordinates:
            file.write(f"{coord[0]}, {coord[1]}\n")
        
def read_overlaps_csv(csv_url):

    # Read file line by line, splitting by the delimiter
    data = []
    with open(csv_url, 'r') as file:
        for line in file:
            data.append(line.strip().split(','))

    # Convert to DataFrame, padding shorter rows with NaN
    df = pd.DataFrame(data)
    df.columns = df.iloc[0]
    df.drop(index=0, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df = df.astype({'Overlap ID':'int32','Thickness':'Float64', 'Area':'Float64', 'Image Count': 'int32'})
     
    return df

def get_serial_image(overlaps_df, row_id, serial=4, image=5):

    serial_lst = []
    img_lst = []

    for i in range(overlaps_df.iloc[row_id]['Image Count']):
        move_rows = i*2
        serial_lst.append(overlaps_df.iloc[row_id,serial+move_rows])
        img_lst.append(overlaps_df.iloc[row_id, image+move_rows])
        
    return serial_lst, img_lst

def handle_null_pixels(img):
    
    img[img<0] = np.nan
    
    return img

def parse_camrange_universal_ground_range(filename):
    # Dictionary to store the parsed values
    parsed_data = {}

    # Regex pattern to capture the group and its content
    group_pattern = re.compile(r'Group\s*=\s*UniversalGroundRange(.*?)End_Group', re.DOTALL)
    feature_pattern = re.compile(r'(\w+)\s*=\s*([\w\.-]+)')

    with open(filename, 'r') as file:
        content = file.read()

        # Search for the specific group
        group_match = group_pattern.search(content)
        if group_match:
            group_content = group_match.group(1)

            # Find all features and their values
            for feature_match in feature_pattern.findall(group_content):
                key, value = feature_match
                # Try to convert to float if possible, otherwise keep as string
                try:
                    value = float(value)
                except ValueError:
                    pass
                parsed_data[key] = value

    return parsed_data
