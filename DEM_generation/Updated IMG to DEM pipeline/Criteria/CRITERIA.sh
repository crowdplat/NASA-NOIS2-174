#!/bin/bash

export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs
echo "export conda envs path"

source activate nasa
echo "nasa env activated"

echo "start criteria"

get_yaml_value() {
    local key=$1
    grep "^$key:" config.yaml | awk -F ': ' '{print $2}' | tr -d '"'
}

url_prefix=$(get_yaml_value "url_prefix")
MINLON=$(get_yaml_value "MINLON")
MAXLON=$(get_yaml_value "MAXLON")
MINLAT=$(get_yaml_value "MINLAT")
MAXLAT=$(get_yaml_value "MAXLAT")
directory_path=$(get_yaml_value "directory_path")

# Print the values
echo "url_prefix: $url_prefix"
echo "MINLON: $MINLON"
echo "MAXLON: $MAXLON"
echo "MINLAT: $MINLAT"
echo "MAXLAT: $MAXLAT"
python $url_prefix/Parser_polygon_overlap_centroids.py

# Define the URL prefix for the CSV file
centroid_file="$url_prefix/acceptable_img_pairs.csv"

# Read the CSV file and store the values in an associative array
declare -A centroids

# Skip the header and read the CSV file line by line
while IFS=',' read -r id base_image1 base_image2 centroid_longitude centroid_latitude centroid_longitude360; do
    # Skip the header line
    if [[ "$id" != "ID" ]]; then
        centroids["$id"]="$base_image1,$base_image2,$centroid_latitude,$centroid_longitude360"
    fi
done < "$centroid_file"

# Loop through each ID in the centroids associative array
for id in "${!centroids[@]}"; do
    echo "Processing ID: $id"
    
    # Read the corresponding values
    IFS=',' read -r base_image1 base_image2 centroid_latitude centroid_longitude360 <<< "${centroids[$id]}"

    # Loop through each .cub file in the specified directory
    for file in $directory_path/*.map.cub; do
        SECONDS=0
        name=$(basename "$file" .map.cub)
        f="${name%.*}"
        echo "Start preprocessing $f for ID $id"

        # Check if the base image names match the current ID
        if [[ "$f" == "$base_image1" || "$f" == "$base_image2" ]]; then
            # Create a unique output filename based on the intersection
            campoint_file="${f}--${centroid_latitude}--${centroid_longitude360}.csv"
            # Run the campt command and capture the output
            campt_output=$(campt from="$url_prefix/experiment/${f}.map.cub" \
                                 latitude="$centroid_latitude" \
                                 longitude="$centroid_longitude360" \
                                 type="Ground" \
                                 to="$campt_output" \
                                 format="FLAT" 2>&1)
#Can be also FLAT
            # Check if the campt command was successful
            if [[ $? -ne 0 ]]; then
                echo "Error running campt for $f: $campt_output"
                break
            fi

            # Write the intersection to the output file
            echo "$campt_output" > "$url_prefix/experiment/$campoint_file"
        fi
    done  # End of the file loop
done  # End of the ID loop
#done  # End of the ID loop
    ################
    ## Stereoimage criteria 1-2 stage
        

python $url_prefix/Criteria1.py 
sort $url_prefix/basenames.lis | uniq > unique_basenames.lis
python $url_prefix/test_overlap.py 



        
