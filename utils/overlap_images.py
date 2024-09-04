def overlap_images():

    import numpy as np
    import pandas as pd
    import os 
    os.chdir('/home/ec2-user/SageMaker/')
    
    from automate_image_criteria import *

    
    overlaps_df = read_overlaps_csv('Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Thomas_practice/Connecting_Ridge_cubs_overlap_stats.csv')
    serial_lst, img_lst = get_serial_image(overlaps_df, row_id=0, serial=4, image=5)
    
    for i in img_list:
        print(i)