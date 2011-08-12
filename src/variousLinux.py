from os.path import join, split
from subprocess import call

SIC_SPOTTY = '/home/basar/Personal/Martin_Seeger/imaging/scripts/spotty.R'
SIC_ROOT = '/home/basar/Personal/Martin_Seeger/working_directory' 
SIC_PROCESSED = "processed"

xc = 348
yc = 260


call(['Rscript', SIC_SPOTTY, '--args', str(xc), str(yc), join(SIC_ROOT, SIC_PROCESSED, 'GFP_P0_T50.tif_INT.txt')])