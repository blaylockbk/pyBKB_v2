# Brian Blaylock
# Version 2 update
# Summer 2015

"""
Download True Color Images from NASA WorldView Aqua and Terra Satellites
and add the time stamp to the image my way of a watermark.
"""

import urllib
from datetime import datetime, timedelta
import numpy as np
import os

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

FONT = 'Arial.ttf'
watermark_label = "THE DATE GOES HERE"	


def add_watermark(in_file, text, out_file='watermark.jpg', angle=0, opacity=0.8):
    img = Image.open(in_file).convert('RGB')
    watermark = Image.new('RGBA', img.size, (0,0,0,0))
    size = 2
    n_font = ImageFont.truetype(FONT, size)
    n_width, n_height = n_font.getsize(text)
    text_size_scale = 1.5
    while n_width+n_height < watermark.size[0]/text_size_scale:
        size += 2
        n_font = ImageFont.truetype(FONT, size)
        n_width, n_height = n_font.getsize(text)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    draw.text(((watermark.size[0] - n_width) / 10,
              (watermark.size[1] - n_height) / 100),
              text, font=n_font)
    watermark = watermark.rotate(angle,Image.BICUBIC)
    alpha = watermark.split()[3 ]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    Image.composite(watermark, img, watermark,).save(out_file, 'JPEG')

if __name__ == "__main__":

    outdir = './sat_images/'

    start_date = datetime(2016,7,18)
    end_date   = datetime(2016,7,21)
    

    # specify the dates you want to retrieve

    date = start_date

    while end_date >= date:
        for sat in np.array(["Terra","Aqua"]): 
            year = str(date.year)
            dayofyear = str(date.timetuple().tm_yday)
            stringdate = datetime.strftime(date,"%Y-%m-%d")         
            
            # Utah        
            URL = "http://map2.vis.earthdata.nasa.gov/image-download?TIME="+year+dayofyear+"&extent=-116.6972484336448,35.054396923451016,-106.9589671836448,43.896193798451016&epsg=4326&layers=MODIS_"+sat+"_CorrectedReflectance_TrueColor,Coastlines,Reference_Features,MODIS_Fires_All&opacities=1,1,1,1&worldfile=false&format=image/jpeg&width=4433&height=4024"
            
            # Utah Lake        
            URL = "http://map2.vis.earthdata.nasa.gov/image-download?TIME="+year+dayofyear+"&extent=-112.251,39.7,-111.35,40.675&epsg=4326&layers=MODIS_"+sat+"_CorrectedReflectance_TrueColor,Coastlines,Reference_Features,MODIS_Fires_All&opacities=1,1,1,1&worldfile=false&format=image/jpeg&width=4433&height=4024"        

            
            #Since the Terra satellite passes over before Aqua
            # we need to save it before Aqua (alphebetical order puts it in wrong order)
            if sat == "Terra":
                sat_order="1Terra"
            if sat == "Aqua":
                sat_order="2Aqua"
            image_name = 'MODIS_TrueColor_'+stringdate+'_'+sat_order+'.jpg'
            urllib.urlretrieve(URL, outdir+image_name)
            add_watermark(outdir+image_name,'MODIS '+sat+' True Color: '+stringdate,outdir+image_name)
            print "Saved", image_name  
        date = date+timedelta(days=1)
