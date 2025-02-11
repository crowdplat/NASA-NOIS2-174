import os
import re
import logging
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.strtree import STRtree

# Create a timestamp for the log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f'Parser_polygon_log_{timestamp}.txt'

# Set up logging
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def parse_latitude_longitude(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Define regex patterns for LatitudeRange and PositiveEast180 groups
    latitude_pattern = r"Group\s*=\s*LatitudeRange.*?MinimumLatitude\s*=\s*([\-\d\.]+).*?MaximumLatitude\s*=\s*([\-\d\.]+)"
    positive_east_pattern = r"Group\s*=\s*PositiveEast180.*?MinimumLongitude\s*=\s*([\-\d\.]+).*?MaximumLongitude\s*=\s*([\-\d\.]+)"

    # Search for the patterns in the content
    latitude_match = re.search(latitude_pattern, content, re.DOTALL)
    positive_east_match = re.search(positive_east_pattern, content, re.DOTALL)

    # Extract values if matches are found
    if latitude_match and positive_east_match:
        min_latitude = float(latitude_match.group(1))
        max_latitude = float(latitude_match.group(2))
        min_longitude = float(positive_east_match.group(1))
        max_longitude = float(positive_east_match.group(2))

        # Extract the base name of the file (without path and extension)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        # Ensure we only take the part before any additional extensions
        base_name = base_name.split('.')[0]  # This will ensure we only keep the first part

        # Create variable names dynamically
        min_latitude_var = f"min_latitude_{base_name}"
        max_latitude_var = f"max_latitude_{base_name}"
        min_longitude_var = f"min_longitude_{base_name}"
        max_longitude_var = f"max_longitude_{base_name}"

        # Assign values to dynamically named variables
        globals()[min_latitude_var] = min_latitude
        globals()[max_latitude_var] = max_latitude
        globals()[min_longitude_var] = min_longitude
        globals()[max_longitude_var] = max_longitude

        # Create the polygon using the coordinates
        polygon = Polygon([
            (min_longitude, min_latitude),  # Bottom-left
            (max_longitude, min_latitude),  # Bottom-right
            (max_longitude, max_latitude),  # Top-right
            (min_longitude, max_latitude),  # Top-left
            (min_longitude, min_latitude)    # Closing the polygon
        ])

        return polygon, base_name, min_latitude_var, max_latitude_var, min_longitude_var, max_longitude_var  # Return polygon, base name, and variable names
    else:
        print(f"Could not find required data in file: {file_path}")
        return None, None, None, None, None, None
def read_basenames(list_path):
    """Read basenames from a given file and return a list."""
    with open(list_path, 'r') as file:
        basenames = [line.strip() for line in file if line.strip()]  # Read and strip lines
    return basenames

def process_directory(directory):
    polygons = []
    basenames = read_basenames('unique_basenames')
    for basename in basenames:
        # Construct the full filename based on the basename
        filename = f"{basename}.camrange.cub.txt"
        for filename in os.listdir(directory):
            if filename.endswith('.camrange.cub.txt') and re.match(r'M\d{9}\.camrange\.cub\.txt', filename):
                file_path = os.path.join(directory, filename)
                polygon, base_name, min_latitude_var, max_latitude_var, min_longitude_var, max_longitude_var = parse_latitude_longitude(file_path)
                if polygon is not None:
                    polygons.append((polygon, base_name, min_latitude_var, max_latitude_var, min_longitude_var, max_longitude_var))  # Store tuple of polygon, base name, and variable names

    return polygons



# Specify the directory containing text files
unique_basenames = config['unique_basenames']
directory_path = config['directory_path_pyt']
polygons_list = process_directory(directory_path)
MINLON=config['MINLON']
MAXLON=config['MAXLON']
MINLAT=config['MINLAT']
MAXLAT=config['MAXLAT']

# Print the number of polygons found
print(f"Total number of polygons found: {len(polygons_list)}")


# Print the polygons for verification
for polygon, base_name, min_lat_var, max_lat_var, min_lon_var, max_lon_var in polygons_list:
    print(f"Polygon for {base_name}: {polygon}")
    
# Extract only the polygons from the polygons_list
polys = [polygon for polygon, base_name, min_lat_var, max_lat_var, min_lon_var, max_lon_var in polygons_list]
base_names = [base_name for polygon, base_name, min_lat_var, max_lat_var, min_lon_var, max_lon_var in polygons_list]


# Create a spatial index
s = STRtree(polys)

# Define the query geometry (representing the site)
query_geom = Polygon([(MINLON, MINLAT), (MAXLON, MINLAT),
                      (MAXLON, MAXLAT), (MINLON, MAXLAT)])

# Query the spatial index for potential intersections
result_indices = s.query(query_geom)

intersections = []
intersection_base_names = []
intersection_areas = []

for index in result_indices:
    intersection = polys[index].intersection(query_geom)
    if not intersection.is_empty:  # Check if the intersection is not empty
        intersections.append(intersection)
        intersection_base_names.append(base_names[index])
        intersection_areas.append(intersection.area)  # Calculate area of intersection


# Output the resulting intersections
for i, inter in enumerate(intersections):
    # Get the base name of the polygon that intersects
    base_name = polygons_list[result_indices[i]][1]
    print(f"Intersection between {base_name} and the site: {inter}")
    
    # Output the areas of the individual intersections with the site
for idx, area in enumerate(intersection_areas):
    print(f"Area of intersection between {intersection_base_names[idx]} and the site: {area}")


# Plotting img1
fig, ax = plt.subplots()

# Plot the original polygons
for poly in polys:
    x, y = poly.exterior.xy
    ax.fill(x, y, alpha=0.6, fc='blue', ec='black')

# Plot the query geometry (the Connecting Ridge)
qx, qy = query_geom.exterior.xy
ax.fill(qx, qy, alpha=0.5, fc='red', ec='black', label='Query Geometry')

# Plot the intersections
for inter in intersections:
    if isinstance(inter, Polygon):
        ix, iy = inter.exterior.xy
        ax.fill(ix, iy, alpha=0.3, fc='green', ec='black', label='Intersection')
    elif isinstance(inter, (LineString, MultiLineString)):
        ix, iy = inter.xy
        ax.plot(ix, iy, color='green', linewidth=2, label='Intersection')

# Set limits for x and y axes
ax.set_xlim(-180, 50)
ax.set_ylim(-90, -86)  # Set y-limits to reflect original values

# Set the aspect ratio
ax.set_aspect('auto')  # Allow stretching along the y-axis

ax.set_title('Site intersecting the image boxes')
#ax.legend()

# Generate a timestamp for the filename
filename_img1 = f"Final_site_intersect_img_boxes_{timestamp}.png"

# Save the figure
plt.savefig(filename_img1, bbox_inches='tight', dpi=300)


#plt.show()

# Now find intersections of intersections
intersection_of_intersections = []
centroids = []
intersection_names = []
intersection_of_intersection_areas = []
Overlap_percentage = []

# Regular expression to match the desired base name format
pattern = re.compile(r'M\d{9}')

for i in range(len(intersections)):
    for j in range(i + 1, len(intersections)):
        inter = intersections[i].intersection(intersections[j])
        if not inter.is_empty:
            base_name_1 = intersection_base_names[i]
            base_name_2 = intersection_base_names[j]
            
            # Check if base names match the specified format
            if (pattern.match(base_name_1) and pattern.match(base_name_2) and 
                base_name_1 == base_name_2):  # Check if they have the same nine digits
                continue  # Skip this intersection of intersections
            
            intersection_of_intersections.append(inter)
            centroids.append(inter.centroid)
            intersection_names.append((intersection_base_names[i], intersection_base_names[j]))
            intersection_of_intersection_areas.append(inter.area)  # Calculate area of intersection of intersections
            
            # Calculate overlap percentages
            area1 = intersection_areas[i]
            area2 = intersection_areas[j]
            overlap_percentage1 = (inter.area / area1) * 100
            overlap_percentage2 = (inter.area / area2) * 100
            
            # Store the smaller percentage
            smaller_overlap_percentage = min(overlap_percentage1, overlap_percentage2)
            Overlap_percentage.append(smaller_overlap_percentage)

# Output the resulting intersections of intersections and their centroids
for idx, inter in enumerate(intersection_of_intersections):
    base_name_1, base_name_2 = intersection_names[idx]
    print(f"Intersection {idx + 1} of {base_name_1} and {base_name_2} inside the site cambox: {inter}")
    print(f"Centroid of intersection {idx + 1} of {base_name_1} and {base_name_2} inside the site cambox: {centroids[idx]}")
    print(f"Area of intersection {idx + 1} of {base_name_1} and {base_name_2} inside the site cambox: {intersection_of_intersection_areas[idx]}")
    print(f"Overlap percentage for intersection {idx + 1} of {base_name_1} and {base_name_2}: {Overlap_percentage[idx]:.2f}%")
#filename_txt = f'acceptable_img_pairs.txt'

#with open(filename_txt, 'w') as file:
#    for idx, inter in enumerate(intersection_of_intersections):
#        if Overlap_percentage[idx] > 30:
#            base_name_1, base_name_2 = intersection_names[idx]
#            #file.write(f"Intersection {idx + 1} of {base_name_1} and ##{base_name_2}: {inter}\n")
#            file.write(f"Centroid of intersection {idx + 1} of {base_name_1} and {base_name_2}: {centroids[idx]}\n")
            #file.write(f"Overlap percentage for intersection {idx + 1} of {base_name_1} and {base_name_2}: {Overlap_percentage[idx]:.2f}%\n\n")

#print(f"For Common Image Stereo Overlap greater than 30%, the Centroids of intersections are written to {filename_txt}")
def convert_longitude(lon):
    return (lon + 360) % 360

filename_csv = f'accepted_img_pairs.csv'
fieldnames = ['ID', 'BASE_IMAGE1', 'BASE_IMAGE2', 'CENTROID_LONGITUDE', 'CENTROID_LATITUDE', 'CENTROID_LONGITUDE360']
with open(filename_csv, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for idx, inter in enumerate(intersection_of_intersections):
        if Overlap_percentage[idx] > 30:
            base_name_1, base_name_2 = intersection_names[idx]
            centroid_longitude = centroids[idx].x
            centroid_latitude = centroids[idx].y
            centroid_longitude360 = convert_longitude(centroid_longitude)
            writer.writerow({
                    'ID': idx + 1,
                    'BASE_IMAGE1': base_name_1,
                    'BASE_IMAGE2': base_name_2,
                    'CENTROID_LONGITUDE': centroid_longitude,
                    'CENTROID_LATITUDE': centroid_latitude,
                    'CENTROID_LONGITUDE360': centroid_longitude360
                })

print(f"For Common Image Stereo Overlap greater than 30%, the centroids of intersections are written to {filename_csv}")









# Plotting img2
fig, ax = plt.subplots()

# Plot the original polygons
#for poly in polys:
 #   x, y = poly.exterior.xy
 #   ax.fill(x, y, alpha=0.6, fc='blue', ec='black')

# Plot the query geometry (the Connecting Ridge)
qx, qy = query_geom.exterior.xy
ax.fill(qx, qy, alpha=0.5, fc='red', ec='black', label='Query Geometry (Connecting Ridge)')

# Plot the intersections
for inter in intersections:
    if isinstance(inter, Polygon):
        ix, iy = inter.exterior.xy
        ax.fill(ix, iy, alpha=0.3, fc='green', ec='black', label='Intersection')
    elif isinstance(inter, (LineString, MultiLineString)):
        ix, iy = inter.xy
        ax.plot(ix, iy, color='green', linewidth=2, label='Intersection')

# Plot the intersections of intersections
for inter in intersection_of_intersections:
    if isinstance(inter, Polygon):
        ix, iy = inter.exterior.xy
        ax.fill(ix, iy, alpha=0.4, fc='green', ec='black', label='Intersection')
    elif isinstance(inter, (LineString, MultiLineString)):
        ix, iy = inter.xy
        ax.plot(ix, iy, color='green', linewidth=2, label='Intersection')

# Plot centroids
for centroid in centroids:
    if isinstance(centroid, Point):
        ax.plot(centroid.x, centroid.y, 'ro')  # Plot centroid as red dot

# Set limits for x and y axes
ax.set_xlim(-180, -100)
ax.set_ylim(-90, -89)  # Set y-limits to reflect original values

# Set the aspect ratio
ax.set_aspect('auto')  # Allow stretching along the y-axis

ax.set_title('Image boxes intersections') 
#ax.legend()

# Generate a timestamp for the filename
filename_img2 = f"Final_Img_boxes_intersect_img_boxes_{timestamp}.png"

# Save the figure
plt.savefig(filename_img2, bbox_inches='tight', dpi=300)

#plt.show()

# Log the completion of the processing
logging.info(f"Graph of Connecting Ridge intersecting the image boxes is {filename_img1}")
logging.info(f"Graph of image boxes intersecting the image boxes inside the Connecting Ridge is {filename_img2}")
logging.info(f"For Common Image Stereo Overlap greater than 30%, the Centroids of intersections are written to {filename_csv}")
logging.info("Completed processing all files in the directory.")