#!/bin/bash

export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs
echo "export conda envs path"

source activate nasa
echo "nasa env activated"

echo "start batch processing"


#For processing other sites
#if [ "$#" -ne 1 ]; then
#    echo "Usage: $0 <site_name> <Other Prefix>"
#    exit 1
#fi



# Assign the input file and sample size to variables
#site_name='Connecting_Ridge'
#default_value='/Viktoriia_practice'
#other_prefix=${2:-${default_value}}
#echo "Site entered: $site_name"
#echo "Other Prefix entered: $other_prefix"
#echo "url_prefix: $url_prefix"

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

#Connecting Ridge
#MINLON=-172.318538
#MAXLON=-102.226492
#MINLAT=-89.835617
#MAXLAT=-89.068587

echo "site bounding box"
echo "MINLAT = $MINLAT  MAXLAT = $MAXLAT MINLON = $MINLON MAXLON = $MAXLON"
echo "-----------------"

#python $url_prefix/utils/download_imgs.py

#This is a shape for spice
# Warning: there is an option to use 5M or 10M instead of 20M but the processing time increases drastically

pds2isis from=$shape_path/LDEM_875S_20M_FLOAT.LBL to=$shape_path/LDEM_875S_20M_FLOAT.cub
fx f1=$shape_path/LDEM_875S_20M_FLOAT.cub equation="f1*1000" to=$shape_path/LDEM_875S_20M_FLOAT.meters.cub
demprep from=$shape_path/LDEM_875S_20M_FLOAT.meters.cub to=$shape_path/LDEM_875S_20M_FLOAT.demprep.cub


#mosrange fromlist=mosaic_level_1.lis to=mosaic.map projection=equirectangular 
#maptemplate check documentation
#polar stereographic option
# CLON CLAT

#no need to camtrim
#(or create a map file using maptemplate)
#Light time correction


#INS-85600_CONSTANT_TIME_OFFSET = ( 0.0 )
#INS-85610_CONSTANT_TIME_OFFSET = ( 0.0 )


for file in $img_prefix/*.IMG


do 
    SECONDS=0 
    name=$(basename "$file" .IMG)
    f="${name%.*}"
          all_list_file="$directory_path/all_list.lis"
   
   # Add the  file path to the list
    echo "$directory_path/${f}.map.cub" >> "$all_list_file"
    
    
done

for file in $img_prefix/*.IMG
do 
    SECONDS=0 
    name=$(basename "$file" .IMG)
    f="${name%.*}"
    f="${f::-2}"
    if [ ! -f "$directory_path/${f}.map.cub" ]; then
        echo "start preprocessing $f"
        lronac2isis from = $img_prefix/${f}LE.IMG     to = $directory_path/${f}LE.raw.cub
        lronac2isis from = $img_prefix/${f}RE.IMG     to = $directory_path/${f}RE.raw.cub
        echo "complete lronac2isis"
        #spiceinit   from = $directory_path/${f}.raw.cub spksmithed=true shape=ELLIPSOID ckpredicted=true
    spiceinit   from = $directory_path/${f}LE.raw.cub spksmithed=true shape=user model=$shape_path/LDEM_875S_20M_FLOAT.demprep.cub
    spiceinit   from = $directory_path/${f}RE.raw.cub spksmithed=true shape=user model=$shape_path/LDEM_875S_20M_FLOAT.demprep.cub
    
    #shape=user model=$url_prefix/shape/LDEM_875S_5M_FLOAT.demprep.cub
    #shape = ellipsoid use user shape instead
    #might try NAC_DTM
    #web=true not working
    
        echo "complete spiceinit"
    

        lronaccal   from = $directory_path/${f}LE.raw.cub     to = $directory_path/${f}LE.cal.cub
        lronaccal   from = $directory_path/${f}RE.raw.cub     to = $directory_path/${f}RE.cal.cub
    #calibrates pixel values, can switch to radiance RadiometricType=radiance
        echo "complete lronaccal"

        lronacecho  from = $directory_path/${f}LE.cal.cub to = $directory_path/${f}LE.echo.cub
        lronacecho  from = $directory_path/${f}RE.cal.cub to = $directory_path/${f}RE.echo.cub
        echo "complete lronacecho"
        #Uncomment for stitching the left and right images
        #handmos from=$directory_path/${f}LE.echo.cub mosaic=$directory_path/${f}.mos.cub priority=band criteria=greater
        #handmos from=$directory_path/${f}RE.echo.cub mosaic=$directory_path/${f}.mos.cub priority=band criteria=greater
        #handmos $directory_path/${f}RE.echo.cub mosaic=$directory_path/${f}.mos.cub priority=band criteria=greater
        
        cam2map from=$directory_path/${f}LE.echo.cub to=$directory_path/${f}LE.map.cub map=$map matchmap=true
        cam2map from=$directory_path/${f}RE.echo.cub to=$directory_path/${f}RE.map.cub map=$map matchmap=true
        
        echo "complete cam2map"
        
        
        #mapmos $directory_path/${f}LE.map.cub mosaic=$directory_path/${f}.mos.cub priority=band criteria=greater
        #mapmos $directory_path/${f}RE.map.cub mosaic=$directory_path/${f}.mos.cub priority=band criteria=greater
   
   # Trim the left NAC image
   # if [[ "$f" == *"L"* ]]; then
        #trim from=$directory_path/${f}.echo.cub to=$directory_path/${f}.tr.cub left=46 right=26
        #echo "Complete trimming left NAC: ${f}.tr.cub"
    #fi

    # Trim the right NAC image
    #if [[ "$f" == *"R"* ]]; then
        #trim from=$directory_path/${f}.echo.cub to=$directory_path/${f}.tr.cub left=26 right=46
        #echo "Complete trimming right NAC: ${f}.tr.cub"
    #fi
   ########################
   #experimetal
   #photometric correction
   #lronacpho from=$url_prefix/experiment/${f}.tr.cub to=$url_prefix/experiment/${f}.pho.cub phopar=$url_prefix/basicpho.pvl
   #or nacpho.pvl
   #check with no trim
   

    
    #need to add reduction
    
   #might or LE and RE or do later after stereo pipeline
       
   
   
   
   
   #\
#warpalgorithm=forwardpatch patchsize=50
#automosaic everything
   
    
    #experimental
    #coregistration
  
    

    
#lronac2mosaic.py 8.8.5 https://stereopipeline.readthedocs.io/en/latest/examples/lronac.html


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
    
    
    
            # camrange 
    #camrange from=${directory_path}/${f}.map.cub to=${directory_path}/${f}.camrange.cub 
    #echo "complete camrange"
    # capture python output and get lat long range
    #output=$(python ${url_prefix}/parse_camrange.py --file_url "${url_prefix}/camrange/${f}.camrange.cub.txt")
#check projection parameters
    else
        echo "Skipping $f: $directory_path/${f}.map.cub already exists"
    fi
  

done
############


echo "complete batch processing"
