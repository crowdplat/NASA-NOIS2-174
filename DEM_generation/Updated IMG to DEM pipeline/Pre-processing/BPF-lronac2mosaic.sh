#!/bin/bash

export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs
echo "export conda envs path"

source activate nasa
echo "nasa env activated"

echo "start batch processing"

#Remember to check the config.yaml for the right parameters

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
directory_path=$(get_yaml_value "directory_path")
shape_path=$(get_yaml_value "shape_path")
map=$(get_yaml_value "map")
ames_prefix=$(get_yaml_value "ames_prefix")
custom_footprint=$(get_yaml_value "custom_footprint")


# Print the values
echo "url_prefix: $url_prefix"
echo "MINLON: $MINLON"
echo "MAXLON: $MAXLON"
echo "MINLAT: $MINLAT"
echo "MAXLAT: $MAXLAT"
echo "img_prefix: $img_prefix"



#url_prefix="/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Viktoriia_practice"


total_f=$(ls -lR $img_prefix/*.IMG | wc -l)
echo "total IMG files to be processed:  $total_f"


echo "site bounding box"
echo "MINLAT = $MINLAT  MAXLAT = $MAXLAT MINLON = $MINLON MAXLON = $MAXLON"
echo "-----------------"

#download script for the images

#python $url_prefix/utils/download_imgs.py

#This is a shape for spice, in case if taken the route of the ISIS commands
# Warning: there is an option to use 5M or 10M instead of 20M but the processing time increases drastically

#pds2isis from=$shape_path/LDEM_875S_20M_FLOAT.LBL to=$shape_path/LDEM_875S_20M_FLOAT.cub
#fx f1=$shape_path/LDEM_875S_20M_FLOAT.cub equation="f1*1000" to=$shape_path/LDEM_875S_20M_FLOAT.meters.cub
#demprep from=$shape_path/LDEM_875S_20M_FLOAT.meters.cub to=$shape_path/LDEM_875S_20M_FLOAT.demprep.cub



for file in $img_prefix/*.IMG
do 
    SECONDS=0 
    name=$(basename "$file" .IMG)
    f="${name%.*}"
    f="${f::-2}"
        echo "start preprocessing $f"
        
        "$ames_prefix/lronac2mosaic.py" -o $directory_path/${f} -t 4  "$img_prefix/${f}LE.IMG" "$img_prefix/${f}RE.IMG"
        #-k
 cam2map from=$directory_path/${f}/${f}LE.lronaccal.lronacecho.noproj.mosaic.norm.cub to=$directory_path/${f}.map.cub map=$map matchmap=true
 
 
 if [ "$custom_footprint" = false ]; then
    footprintinit from="$directory_path/${f}.map.cub"
    echo "complete footprintinit"
    # camrange 
    camrange from=${directory_path}/${f}.map.cub to=${directory_path}/${f}.camrange.cub 
    echo "complete camrange"
    
else
    python $url_prefix/coordlist.py
    campt from="$directory_path/${f}.map.cub" \
          usecoordlist=true \
          coordlist=$directory_path/coordlist.txt \
          coordtype="Image" \
          to="$directory_path/${f}.pvl" \
          format="PVL" 2>&1
    awk -F',' '
    NR > 1 && !/Null/ {
        if (!found_first) {
            print $0 > "'$directory_path'/'$f'.camrange.cub.txt"
            found_first = 1
        }
        last_valid = $0
    }
    END {
        if (found_first && last_valid) {
            print last_valid > "'$directory_path'/'$f'.camrange.cub.txt"
        }
    }
' "$directory_path/${f}.pvl"

    
fi

    #the spread used in the coordlist is defined by the specs of camera used, see https://www.lroc.asu.edu/about/specs
          

done
############


echo "complete batch processing"
