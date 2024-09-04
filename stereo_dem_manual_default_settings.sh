# default parameters same as https://stereopipeline.readthedocs.io/en/stable/examples/lronac.html

img1=/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Thomas_practice/cubs/M104318871LE.cal.echo.cub
img2=/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Thomas_practice/cubs/M104311715LE.cal.echo.cub

# datetime
dt=$(date '+%d%m%Y-%H%M%S')


echo "start parellel_stereo (default)  with img1: $img1 and img2:$img2"
SECONDS=0 

# parallel_stereo 

parallel_stereo $img1 $img2  \
  --alignment-method affineepipolar                \
  run_default_{$dt}/run

echo "complete parellel_stereo (default) with img1: $img1 and img2:$img2 in $SECONDS seconds"

echo "start point2dem (default)"
SECONDS=0 
point2dem --stereographic --auto-proj-center \
  --errorimage --orthoimage                 \
    run_default_{$dt}/run-PC.tif run_default/run-L.tif


echo "complete point2dem (default) in $SECONDS seconds"

echo "DEM created"
