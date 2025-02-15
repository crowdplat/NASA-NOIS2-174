# Goal

The project contains three parts:
1. Selecting the images for DEMs production
2. Producing DEMs with open source [ISIS](https://isis.astrogeology.usgs.gov/8.3.0/) and [ASP](https://stereopipeline.readthedocs.io/en/latest/index.html) pipelines
3. Upscaling DEMs using the DL model

# Enivronment

This project is run on AWS SageMaker Notebook with ml.g4dn.xlarge instance. anaconda is used to create the environment from exisiting pytorch environment `pytorch_p310` in AWS for reusability 

 <div align="center">
 <img src="images/zoomed_sample.png" width="75%" alt="Sample Output and Difference Map">
 </div>


# Preprocessing

#


# Training data source 
https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/


# Model

Default parameters: Scaling Factor 2x (Changeable) 
Model architecture - Generative Adversarial Network (GAN):  
- Generator: Encoder-Decoder with Attention layers
- Discriminator: VGG net


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
