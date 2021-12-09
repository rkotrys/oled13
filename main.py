#!/usr/bin/python
# -*- coding:utf-8 -*-

import SH1106
import time, subprocess
import config
import traceback
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont

def getip():
    ip="- no IP -"
    for dev in ('eth0','wlan0'):
        w=str( subprocess.run(["ip -4 a l "+dev+"|grep inet"], shell=True, capture_output=True, text=True ).stdout ).split()
        if( len(w)>1 ):
            ip = w[1]
            break
    return ip            

def show_clock():
    image = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('fonts/cour.ttf', 26)
    font10 = ImageFont.truetype('fonts/cour.ttf',12)
    now = datetime.now() # current date and time
    buf = now.strftime("%H:%M:%S")
    (sx,sy)=font.getsize(buf)
    draw.text( ( int((128-sx)/2), 5 ), buf, font = font, fill = 0)
    ip=getip()
    (sx,sy)=font10.getsize(ip)
    draw.text((int((128-sx)/2),52), ip, font = font10, fill = 0)
    return image
    
    

try:
    disp = SH1106.SH1106()
    # Initialize library.
    disp.Init()
    disp.clear()

    while True:
        image = show_clock()
        #image=image.rotate(180) 
        disp.ShowImage(disp.getbuffer(image))
        time.sleep(1)

except IOError as e:
    print(e)
    
except KeyboardInterrupt:    
#    config.module_exit()
    exit()
