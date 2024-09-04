#!/bin/bash

echo "start batch processing"



if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <site_name>"
    exit 1
fi



# Assign the input file and sample size to variables
site_name=$1
url_prefix="/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/${site_name}"
echo "Site entered: $site_name"
echo "url_prefix: $url_prefix"

total_f=$(ls -lR $url_prefix/Thomas_practice/imgs_sample/*.IMG | wc -l)
echo "total IMG files to be processed:  $total_f"
# need to capture errors and output an error image list
# camtrim - make sure it is reading the right coordinates

MINLON=-172.318538
MAXLON=-102.226492
MINLAT=-89.835617
MAXLAT=-89.068587

echo "site bounding box"
echo "MINLAT = $MINLAT  MAXLAT = $MAXLAT MINLON = $MINLON MAXLON = $MAXLON"
echo "-----------------"

for file in $url_prefix/Thomas_practice/imgs_sample/*.IMG


do 
    SECONDS=0 
    # echo "test $file"
    name=$(basename "$file" .IMG)
    f="${name%.*}"
    echo "start preprocessing $f"
    lronac2isis from = $url_prefix/Thomas_practice/imgs_sample/${f}.IMG     to = $url_prefix/Thomas_practice/cubs_sample/${f}.cub
    echo "complete lronac2isis"
    spiceinit   from = $url_prefix/Thomas_practice/cubs_sample/${f}.cub shape = ellipsoid
    echo "complete spiceinit"
    lronaccal   from = $url_prefix/Thomas_practice/cubs_sample/${f}.cub     to = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.cub
    echo "complete lronaccal"

    lronacecho  from = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.cub to = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.echo.cub
    echo "complete lronacecho"

    footprintinit from = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.echo.cub
    echo "complete footprintinit"

    # camtrim
    camtrim from = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.echo.cub to = $url_prefix/Thomas_practice/cubs_sample/${f}.cal.echo.trim.cub  MINLAT = $MINLAT  MAXLAT = $MAXLAT MINLON = $MINLON MAXLON = $MAXLON
    echo "complete camtrim"
    
    # campt
    campt from=$url_prefix/Thomas_practice/cubs_sample/${f}.cal.echo.trim.cub to=$url_prefix/Thomas_practice/cubs_sample/${f}-campt.txt format="FLAT"
    echo "complete campt"
    echo "-----------------"
    
    
    echo "complete preprocessing $f in $SECONDS seconds"
done


echo "complete batch processing"