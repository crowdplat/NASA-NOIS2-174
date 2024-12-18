# create conda environment

1. run "conda env list" to check if the env "nasa_tt_pytorch" is there, it should show the directory "/home/ec2-user/SageMaker/envs/nasa_tt_pytorch"

  *if no env "nasa_tt_pytorch", clone to create one, make sure to provide a prefix after -p*
  conda create  -p /home/ec2-user/SageMaker/envs/nasa_tt_pytorch  --clone pytorch_p310    

2. run "export CONDA_ENVS_PATH=/home/ec2-user/SageMaker/envs" 
3. do "conda activate nasa_tt_pytorch" or "source activate nasa_tt_pytorch"
---

# install extra packages

pip install rasterio
pip install ipykernel
pip install wandb

*IMPORTANT - pytorch has error with numpy version, please install version lower than 2 for numpy*

pip install "numpy<2"

# ipython resgister

python -m ipykernel install --user --name nasa_tt_pytorch --display-name "Python (nasa_super_res_pytorch)"

# DEMs source 
https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/

Train Set (training)
NAC_DTM_FECNDITATS3
NAC_DTM_MRINGENII
NAC_DTM_LICHTENBER13
NAC_DTM_ARISTARCHU2

Test Set (validation)
NAC_DTM_VIRTANEN2
NAC_DTM_MESSIER3
NAC_DTM_CMPTNBELK2
