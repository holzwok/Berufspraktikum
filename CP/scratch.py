import Image, ImageDraw
import os
import sys
from os.path import join, exists

print os.getcwd()

outpath = r"C:\Users\MJS\Dropbox\Studium\Berufspraktikum\test_for_idlmerger\out"
filename = "out.MAX_SIC1_stR610_CLB5_stQ570_Whi5_100pc_NG1000ms_0_4M_15min_5_w4Qusar610.tif"
filepath = join(outpath, filename)


def write_into(filename, text, x, y):
    im = Image.open(filename)
    draw = ImageDraw.Draw(im)
    draw.text((x, y), text) #, font=font)
    del draw 
    im.save(filename)
    
    
write_into(filepath, "hallo", 10, 10)