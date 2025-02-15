# Conda Env

1. run "conda env list" to check if the env "nasa_tt_pytorch" is there, it should show the directory "/home/ec2-user/SageMaker/envs/nasa_tt_pytorch"
2. if nasa is not there, run "export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs" 
3. do "conda activate nasa_tt_pytorch" or "source activate nasa_tt_pytorch"
---


1. conda actiate nasa_tt

sh-4.2$ conda env list
# conda environments:

base                     /home/ec2-user/anaconda3
JupyterSystemEnv      *  /home/ec2-user/anaconda3/envs/JupyterSystemEnv
R                        /home/ec2-user/anaconda3/envs/R
python3                  /home/ec2-user/anaconda3/envs/python3
pytorch_p310             /home/ec2-user/anaconda3/envs/pytorch_p310
tensorflow2_p310         /home/ec2-user/anaconda3/envs/tensorflow2_p310

## if no env "nasa_tt_pytorch", clone to create one
## make sure to provide a prefix
conda create  -p /home/ec2-user/SageMaker/envs/nasa_tt_pytorch  --clone pytorch_p310    


# install packages

pip install rasterio
pip install ipykernel
pip install wandb

## IMPORTANT - pytorch has error with numpy version, please install version lower than 2 for numpy

pip install "numpy<2"


# piq manual install and edit piq/ms_ssim.py
 ~/anaconda3/envs/nasa_tt_pytorch/lib/python3.10/site-packages/piq/ms_ssim.py

git clone https://github.com/photosynthesis-team/piq.git
cd piq
python setup.py install --user

in ms_ssim.py:
comment: 
    _validate_input([x, y], dim_range=(4, 5), data_range=(0, data_range))
added:
    data_range = (np.nanmin([x,y]), np.nanmax([x,y]))

2. download and unzip the open source model code reponsitory 


2. ipython register
*first activate conda env*
source activate nasa_tt_pytorch

*then type following*
python -m ipykernel install --user --name nasa_tt_pytorch --display-name "Python (nasa_super_res_pytorch)"



# image source 
https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/



1. Methodologies


global information suplement 
Kriging method
autocorrelation


variogram
GDAL: https://gdal.org/en/latest/download.html
conda install -c conda-forge gdal


Train
NAC_DTM_FECNDITATS3
NAC_DTM_MRINGENII
NAC_DTM_LICHTENBER13
NAC_DTM_ARISTARCHU2

test
NAC_DTM_VIRTANEN2
NAC_DTM_MESSIER3
NAC_DTM_CMPTNBELK2

# Super Resolution model's performance analysis
1. Input and Output Comparison

    - The first panel (LR) represents the low-resolution input DEM (128×128).
    -  While the second panel (HR) corresponds to the high-resolution ground truth DEM (256×256). 
    - The third panel (SR) displays the model-generated super-resolved DEM (256×256).
    - The final panel illustrates the absolute difference between HR and SR, highlighting the discrepancy between the ground truth and the model's output.
    
     The color bars indicate the elevation values, showcasing the depth variations across the DEMs. The mean absolute difference between HR and SR is computed, quantifying the model's reconstruction accuracy.


![Sample Outpur and Difference Map](images/sample_ouput.png)


2. Detailed Visual Analysis

    Comparison of Low-Resolution and Super-Resolution DEMs


 <div align="center">
 <img src="images/zoomed_sample.png" width="75%" alt="Sample Output and Difference Map">
 </div>
