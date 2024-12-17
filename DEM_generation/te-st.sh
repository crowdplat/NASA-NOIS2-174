#!/bin/bash

export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs
echo "export conda envs path"

source activate nasa




# Assign the input file and sample size to variables
site_name='Connecting_Ridge'
default_value='/Viktoriia_practice'
other_prefix=${2:-${default_value}}

url_prefix="/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/${site_name}${other_prefix}"
echo "Site entered: $site_name"
echo "Other Prefix entered: $other_prefix"
echo "url_prefix: $url_prefix"

chmod +x $url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/parallel_stereo
left_image="$url_prefix/cubs_sample/M140869717RE.cal.echo.cub"
right_image="$url_prefix/cubs_sample/M140876512RE.cal.echo.cub"
output_prefix="$url_prefix/cubs_sample/run14"  # Change this to your desired output prefix

   
   echo "Running parallel_stereo"
#"$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/parallel_stereo" \
#    "$left_image" "$right_image" "$output_prefix"

   
   
   #https://stereopipeline.readthedocs.io/en/latest/examples.html
   #https://stereopipeline.readthedocs.io/en/latest/examples/lronac.html
  
 echo "Finished running parallel_stereo"

echo "Running point2dem"

#$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/point2dem -r moon             \
#  --stereographic             \
#  --proj-lon 0 --proj-lat -90 \
 # $url_prefix/cubs_sample/run14-PC.tif
echo "Finished running point2dem"


echo "Started running colormap"
#$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/colormap $url_prefix/cubs_sample/runPC-DEM.tif -o colorized.tif


#$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/colormap $url_prefix/cubs_sample/run14-DEM.tif --hillshade -o color-shaded.tif

#-s shaded.tif

echo "Finished running colormap"

#$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/dem_mosaic $url_prefix/accept/color-shaded_HILLSHADE.tif $url_prefix/color-shaded_HILLSHADE.tif -o blended.tif

echo "Started running colormap"


$url_prefix/ames_stereo_pipeline/StereoPipeline-3.5.0-alpha-2024-07-24-x86_64-Linux/bin/colormap $url_prefix/blended.tif --hillshade -o FINAL_color-shaded.tif

#-s shaded.tif

echo "Finished running colormap"