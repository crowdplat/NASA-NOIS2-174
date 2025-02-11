import pandas as pd
import numpy as np
import math
import re
import os
import csv


def parse_yaml(file_path):
    config = {}
    with open(file_path, 'r') as file:
        current_key = None
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            if ':' in line:  # Key-value pair
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                config[key] = value

    return config

# Load the YAML file
config = parse_yaml('config.yaml')


##############
#Stage 1
#############
def parse_file(file_path):
    # Extract the filename without extension
    filename = os.path.basename(file_path)
    # Updated regex pattern to match M followed by 9 digits and ending with .csv
    match = re.match(r'M\d{9}.*\.csv', filename)
    
    if not match:
        print(f"Filename {filename} does not match the expected pattern.")
        return None

    # Read the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regex to find the required variables
    phase_match = re.search(r'Phase\s*=\s*([-+]?\d*\.\d+|\d+)', content)
    incidence_match = re.search(r'Incidence\s*=\s*([-+]?\d*\.\d+|\d+)', content)
    emission_match = re.search(r'Emission\s*=\s*([-+]?\d*\.\d+|\d+)', content)
    resolution_match = re.search(r'SampleResolution\s*=\s*([-+]?\d*\.\d+|\d+)', content)
    scazgnd_match = re.search(r'SubSpacecraftGroundAzimuth\s*=\s*([-+]?\d*\.\d+|\d+)', content)
    sunazgnd_match = re.search(r'SubSolarGroundAzimuth\s*=\s*([-+]?\d*\.\d+|\d+)', content)


    # Check if matches were found
    if not phase_match or not incidence_match or not emission_match or not resolution_match or not scazgnd_match or not sunazgnd_match:
        print(f"Could not find required variables in {filename}.")
        return None

    # Extract the values
    phase = float(phase_match.group(1))  # Convert to float for scoring
    incidence = float(incidence_match.group(1))  # Convert to float for scoring
    emission = float(emission_match.group(1))  # Convert to float for scoring
    resolution = float(resolution_match.group(1))
    scazgnd = float(scazgnd_match.group(1))
    sunazgnd = float(sunazgnd_match.group(1))

    # Create variable names based on the first 12 characters of the filename
    short_filename = filename[:12]  # Get the first 12 characters

    # Extract latitude and longitude from the filename
    lat_match = re.search(r'(?<=--)(\d{3}\.\d{12})', filename)  # Updated regex for latitude
    long_match = re.search(r'(?<=--)(-?\d+\.\d+)', filename)  # Assuming longitude is still the same


    latitude = float(lat_match.group(0)) if lat_match else None
    longitude = float(long_match.group(0)) if long_match else None

    # Calculate the scores for Phase, Incidence, and Emission
    score_phase = calculate_phase_score(phase)
    score_incidence = calculate_incidence_score(incidence)
    score_emission = calculate_emission_score(emission)
    
    # Calculate total score
    total_score = score_phase + score_incidence + score_emission

    return {
        'basename': short_filename,
        'longitude': longitude,  # Store the extracted longitude
        'latitude': latitude,     # Store the extracted latitude
        'score': total_score,
        'resolution': resolution,
        'SubSpacecraftGroundAzimuth': scazgnd,
        'SubSolarGroundAzimuth': sunazgnd,
        'incidence': incidence,
        'emission': emission,
        'phase': phase
    }

# Function to calculate the score based on Phase value
def calculate_phase_score(phase):
    if 15 <= phase <= 120:
        return 0.5
    else:
        return 0.0

# Function to calculate the score based on Incidence value
def calculate_incidence_score(incidence):
    if 40 <= incidence <= 65:
        return 0.5
    elif 30 <= incidence <= 75:
        return 0.4
    elif 25 <= incidence <= 80:
        return 0.3
    elif 20 <= incidence <= 85:
        return 0.2
    elif 15 <= incidence <= 87.5:
        return 0.1
    else:
        return 0.0

# Function to calculate the score based on Emission value
def calculate_emission_score(emission):
    if 0 <= emission < 40:
        return 1.0
    elif 40 <= emission < 50:
        return 0.5
    else:
        return 0.0

# Directory containing the CSV files
directory = config['directory_path_pyt']

# List to hold data for CSV output
csv_data = []

# Iterate over all CSV files in the directory
for filename in os.listdir(directory):  # Uncomment this line
    if filename.endswith('.csv'):
        file_path = os.path.join(directory, filename)
        parsed_data = parse_file(file_path)
        if parsed_data and parsed_data['score'] >= 0.5:

            emission_rad = math.radians(parsed_data['emission'])  # Convert degrees to radians
            scazgnd_rad = math.radians(parsed_data['SubSpacecraftGroundAzimuth'])  # Convert degrees to radians
            incidence_rad = math.radians(parsed_data['incidence'])
            sunazgnd_rad = math.radians(parsed_data['SubSolarGroundAzimuth'])
            
            # Calculate px and py
            px = -math.tan(emission_rad) * math.cos(scazgnd_rad)
            py = math.tan(emission_rad) * math.sin(scazgnd_rad)
            
            #Calculate shx, shy
            shx = -math.tan(incidence_rad) * math.cos(sunazgnd_rad)
            shy = math.tan(incidence_rad) * math.sin(sunazgnd_rad)

            # Append data to the list for CSV
            csv_data.append({
                'ID_criteria': len(csv_data) + 1,  
                'basename': parsed_data['basename'],  
                'longitude': parsed_data['longitude'],  
                'latitude': parsed_data['latitude'],    
                'score': parsed_data['score'],
                'resolution': parsed_data['resolution'],
                'incidence': parsed_data['incidence'],
                'emission': parsed_data['emission'],
                'phase': parsed_data['phase'],
                'scazgnd': parsed_data['SubSpacecraftGroundAzimuth'],
                'sunazgnd': parsed_data['SubSolarGroundAzimuth'],
                'px': px,
                'py': py,
                'shx': shx,
                'shy': shy
            })

# Save the data to a CSV file
with open('Passed_Criteria_1.csv', 'w', newline='') as csvfile:
    fieldnames = ['ID_criteria', 'basename', 'longitude', 'latitude', 'score', 'resolution', 'incidence', 'emission', 'phase', 'scazgnd', 'sunazgnd', 'px', 'py', 'shx', 'shy']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in csv_data:
        writer.writerow(row)

# Print the results to confirm
for row in csv_data:
    print(row)
    
    #################
    #Stage2
    #############

# Load the CSV file
df = pd.read_csv('Passed_Criteria_1.csv')

# Check the structure of the DataFrame
print("Original DataFrame:")
print(df.head())

# Remove rows where 'latitude' is empty
df = df[df['latitude'].notna()]

# Remove duplicate rows
df = df.drop_duplicates()
df = df.dropna()

# Check the structure of the DataFrame after cleaning
print("DataFrame after removing empty latitudes and duplicates:")
print(df.head())

# Remove rows based on resolution criteria
# Identify basenames to remove
basenames_to_remove = df[(df['resolution'] < 0.5) | (df['resolution'] > 1.7)]['basename'].unique()

# Filter out rows with those basenames
df = df[~df['basename'].isin(basenames_to_remove)]

# Group by latitude and longitude
grouped = df.groupby(['latitude', 'longitude'])

# Create a new list to store pairs
pairs = []

# Create a set to track seen latitude and longitude pairs
seen_pairs = set()

# Iterate through each group
for (lat, lon), group in grouped:
    if (lat, lon) in seen_pairs:
        continue  # Skip if this pair has already been processed

    if len(group) >= 2:  # Only consider groups with at least two entries
        # Get the first two entries
        entry1 = group.iloc[0]
        entry2 = group.iloc[1]
        
        # Calculate the sum of scores for the first two entries only
        score_sum = entry1['score'] + entry2['score']
        
        # Calculate the ratio of resolutions
        resolution_ratio = entry1['resolution'] / entry2['resolution']
        #print(f"Resolution 1: {entry1['resolution']}, Resolution 2: {entry2['resolution']}, Ratio: {resolution_ratio}")
        
        dp = np.sqrt((entry1['px'] - entry2['px']) ** 2 + (entry1['py'] - entry2['py']) ** 2)
        
        #if 0.4 <= dp <= 0.6:
            #dp_score = 5.0
        #elif (0.3 <= dp < 0.4) or (0.6 < dp <= 0.7):
            #dp_score = 2.0
        #else:
            #dp_score = 0.0

        if 0.4 <= dp <= 0.6:
            dp_score = 5.0
        elif 0.3 < dp < 0.4:
            dp_score = 5.0 - (dp - 0.3) * (5.0 - 2.0) / (0.4 - 0.3)  # Linear interpolation from 5.0 to 2.0
        elif 0.2 < dp <= 0.3:
            dp_score = 4.0 - (dp - 0.2) * (4.0 - 2.0) / (0.3 - 0.2)  # Linear interpolation from 4.0 to 2.0
        elif 0.1 < dp <= 0.2:
            dp_score = 3.0 - (dp - 0.1) * (3.0 - 0.0) / (0.2 - 0.1)  # Linear interpolation from 3.0 to 0.0
        elif 0.6 < dp <= 0.7:
            dp_score = 2.0 - (dp - 0.6) * (2.0 - 0.0) / (0.7 - 0.6)  # Linear interpolation from 2.0 to 0.0
        elif 0.7 < dp <= 0.8:
            dp_score = 2.0 - (dp - 0.7) * (2.0 - 0.0) / (0.8 - 0.7)  # Linear interpolation from 2.0 to 0.0
        elif 0.8 < dp <= 0.9:
            dp_score = 3.0 - (dp - 0.8) * (3.0 - 0.0) / (0.9 - 0.8)  # Linear interpolation from 3.0 to 0.0
        elif 0.9 < dp <= 1.0:
            dp_score = 0.0  # Score is 0.0 for dp > 0.9
        else:
            dp_score = 0.0  # Default case
            
        dsh = np.sqrt((entry1['shx'] - entry2['shx']) ** 2 + (entry1['shy'] - entry2['shy']) ** 2)
        #if 0 <= dsh <= 0.1:
            #dsh_score = 5.0
        #elif 0.1 <= dp < 0.2:
            #dsh_score = 2.0
        #else:
            #dsh_score = 0.0
        if 0 <= dsh <= 0.1:
            dsh_score = 5.0
        elif 0.1 < dsh <= 0.2:
            dsh_score = 5.0 - (dsh - 0.1) * (5.0 - 2.0) / (0.2 - 0.1)  # Linear interpolation from 5.0 to 4.0
        elif 0.2 < dsh <= 0.3:
            dsh_score = 2.0 - (dsh - 0.2) * (2.0 - 1.0) / (0.3 - 0.2)  # Linear interpolation from 4.0 to 3.0
        elif 0.3 < dsh <= 0.4:
            dsh_score = 1.0 - (dsh - 0.3) * (1.0 - 0.5) / (0.4 - 0.3)  # Linear interpolation from 3.0 to 2.0
        elif 0.4 < dsh <= 0.5:
            dsh_score = 0.5 - (dsh - 0.4) * (0.5 - 0.2) / (0.5 - 0.4)  # Linear interpolation from 2.0 to 1.0
        elif 0.5 < dsh <= 0.6:
            dsh_score = 0.2 - (dsh - 0.5) * (0.2 - 0.1) / (0.6 - 0.5)  # Linear interpolation from 1.0 to 0.5
        elif 0.6 < dsh <= 0.7:
            dsh_score = 0.1 - (dsh - 0.6) * (0.1 - 0.05) / (0.7 - 0.6)  # Linear interpolation from 0.5 to 0.0
        elif 0.7 <= dsh < 0.8:
            dsh_score = 0.05 - (dsh - 0.7) * (0.05 - 0.01) / (0.8 - 0.7)  # Score is 0.0 for dsh > 0.7
        elif 0.8 <= dsh < 0.9:
            dsh_score = 0.01 - (dsh - 0.8) * (0.01 - 0.0) / (0.9 - 0.08)  # Score is 0.0 for dsh > 0.7
        else:
            dsh_score = 0.0  # Default case
            
        TOTAL = score_sum + dp_score + dsh_score
        print(TOTAL)
       
        if resolution_ratio is not None and (resolution_ratio > 2.5 or resolution_ratio < 0.4):
            continue  # Skip this pair if the ratio is out of bounds
        
        if entry1['basename'][:9] != entry2['basename'][:9]:
        
        # Append the result to the pairs list, including resolutions
            pairs.append({
                'Basename 1': entry1['basename'],
                'Basename 2': entry2['basename'],
                'Score 1 Stage': score_sum,
                'Strength of Stereo': dp_score,
                'Illumination Compatibility': dsh_score,
                'Total Score': TOTAL
            })
        #'ratio': resolution_ratio  # Add the ratio of resolutions
        # Add the pair to the seen set
            seen_pairs.add((lat, lon))

# Create a new DataFrame from the pairs list
pairs_df = pd.DataFrame(pairs)

# Save the new DataFrame to a CSV file
pairs_df.to_csv('Pairs_Criteria_2.csv', index=False)

print("Pairs_Criteria_2.csv has been created.")

#These are the pairs of Images which completed three stage of checks: 1) intersection, 2) Emission, Phase, Incidence checks and 3) dsh, dp checks. Now it is filtered to output the pairs with a score of more than 7

# Read the original CSV file
df = pd.read_csv('Pairs_Criteria_2.csv')

# Filter rows where 'Total Score' is greater than 7
filtered_df = df[(df['Total Score'] > 4) & (df['Illumination Compatibility'] > 0)]

#######
#test
#######
#filtered_df = df

# Select only the required columns
result_df = filtered_df[['Basename 1', 'Basename 2', 'Total Score']]

# Write the result to a new CSV file
result_df.to_csv('Filtered_pairs.csv', index=False)

df = pd.read_csv('Filtered_pairs.csv')

#unique_basenames = set()

# Add basenames from both columns to the set
#unique_basenames.update(df['Basename 1'])
#unique_basenames.update(df['Basename 2'])
# Save the unique basenames to a .lis file
#with open('basenames.lis', 'w') as f:
#    for basename in unique_basenames:
#        print(basename)
#        f.write(f"{basename}\n")

# Write all basenames from 'Basename 1' to basenames1.lis
with open('basenames1.lis', 'w') as f:
    for basename in df['Basename 1']:
        f.write(f"{basename}\n")

# Write all basenames from 'Basename 2' to basenames2.lis
with open('basenames2.lis', 'w') as f:
    for basename in df['Basename 2']:
        f.write(f"{basename}\n")
        
with open('basenames.lis', 'w') as f:
    # Read basenames from basenames1.lis
    with open('basenames1.lis', 'r') as f1:
        for line in f1:
            f.write(line) 

    # Read basenames from basenames2.lis
    with open('basenames2.lis', 'r') as f2:
        for line in f2:
            f.write(line)