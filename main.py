#!/usr/bin/python
# -*- coding:utf-8 -*-

#import SH1106
import time   #, subprocess, sched
#import config
#import traceback
#from datetime import datetime
#from PIL import Image,ImageDraw,ImageFont
from oled13 import oled13

try:
    oled = oled13()
    oled.loop()
    oled.run()
    while True:
        time.sleep(10)

except IOError as e:
    print(e)
    
except KeyboardInterrupt:    
#    config.module_exit()
    exit()
