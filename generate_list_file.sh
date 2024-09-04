#!/bin/bash

# Directory to search for files (change this to your target directory)
DIRECTORY="/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Thomas_practice/cubs/"

# File extension to search for (e.g., .csv)
EXTENSION=".trim.cub"

# Output file where the list of files will be saved
OUTPUT_FILE="Connecting_Ridge_cubs.lis"

# Find all files with the specified extension and save them to the output file
find "$DIRECTORY" -type f -name "*$EXTENSION" > "$OUTPUT_FILE"

echo "List of $EXTENSION files has been saved to $OUTPUT_FILE"
