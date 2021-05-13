from astropy.io import fits                                                     
import numpy as np
import matplotlib.pyplot as plt
import os

folder = '59344'
path = '/data/spectro/lvm/' + folder + '/'

for file in os.listdir(path):
    if file.endswith('fits.gz'):
        hdul = fits.open(path + file)
        image_data = hdul[1].data

    #print(image_data.shape)
    print(hdul[1].header)

    #plt.figure()
    #plt.imshow(image_data, cmap = 'gray')

    hdul.close()

plt.show()

