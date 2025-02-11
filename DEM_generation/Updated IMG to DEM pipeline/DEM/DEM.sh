#!/bin/bash

export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs
echo "export conda envs path"

source activate nasa




get_yaml_value() {
    local key=$1
    grep "^$key:" config.yaml | awk -F ': ' '{print $2}' | tr -d '"'
}

url_prefix=$(get_yaml_value "url_prefix")
MINLON=$(get_yaml_value "MINLON")
MAXLON=$(get_yaml_value "MAXLON")
MINLAT=$(get_yaml_value "MINLAT")
MAXLAT=$(get_yaml_value "MAXLAT")
img_prefix=$(get_yaml_value "img_prefix")
ames_prefix=$(get_yaml_value "ames_prefix")
initial_dem=$(get_yaml_value "initial_dem")
directory_path=$(get_yaml_value "directory_path")
map=$(get_yaml_value "map")

# Print the values
echo "url_prefix: $url_prefix"
echo "MINLON: $MINLON"
echo "MAXLON: $MAXLON"
echo "MINLAT: $MINLAT"
echo "MAXLAT: $MAXLAT"

AVLON=$(echo "scale=6; ($MINLON + $MAXLON) / 2" | bc)
AVLAT=$(echo "scale=6; ($MINLAT + $MAXLAT) / 2" | bc)

# Read the basenames from the files
mapfile -t basenames1 < basenames1.lis
mapfile -t basenames2 < basenames2.lis

chmod +x $ames_prefix/parallel_stereo

# Loop through the basenames
for i in "${!basenames1[@]}"; do
   
    left_image="$directory_path/${basenames1[i]}.map.cub"
    right_image="$directory_path/${basenames2[i]}.map.cub"
    output_prefix="$directory_path/runmap_${i}"  

    echo "Running parallel_stereo for pair $((i + 1))"
 
    "$ames_prefix/parallel_stereo" "$left_image" "$right_image" --alignment-method none -s "$url_prefix/stereo.default" "$output_prefix" 

    # Run point2dem for the output of parallel_stereo
    dem_input="$output_prefix-PC.tif"  
    #_sub
    echo "Running point2dem for $dem_input"

    "$ames_prefix/point2dem" -r moon --errorimage --orthoimage "$dem_input"

    echo "Finished running point2dem for pair $((i + 1))"
    
    
    dem_output="$output_prefix-PC_DEM.tif"
    #dem_outputs+=("$dem_output")
    
done

dem_outputs=()  # Initialize the array

# Print the directory being checked
echo "Looking for files in: $url_prefix/experiment"

# Check if the directory exists
if [[ ! -d "$directory_path" ]]; then
    echo "Error: Directory $directory_path does not exist."
    exit 1
fi

# Populate dem_outputs with existing DEM files from the specified folder
for dem_file in "$directory_path/"*-DEM.tif; do
    echo "Checking file: $dem_file"
    if [[ -f "$dem_file" ]]; then
        dem_outputs+=("$dem_file")  # Add to array if it exists
    else
        echo "File does not exist: $dem_file"
    fi
done

# Check if there are any DEM outputs to process
if [ ${#dem_outputs[@]} -eq 0 ]; then
    echo "No valid DEM outputs found in $directory_path. Exiting."
    exit 1
fi

mosaic_output="$directory_path/mosaic_DEM.tif"
echo "Running dem_mosaic for all DEM outputs"

"$ames_prefix/dem_mosaic" \
    "${dem_outputs[@]}" -o "$mosaic_output"

echo "Finished creating mosaic DEM: $mosaic_output"

#filling the holes
"$ames_prefix/dem_mosaic" \
--fill-search-radius 25 \
--fill-power 8 \
--fill-percent 10 \
--fill-num-passes 3 \
"$mosaic_output" -o $url_prefix/filled.tif
   
#Optional colormap files for human readability   
$ames_prefix/colormap $directory_path/mosaic_DEM.tif --hillshade -o $url_prefix/color-shaded_mosaic_DEM.tif
