#!/usr/bin/python
# -*- coding:utf-8 -*-

import SH1106
import time, sched
import config
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
from helper import getip

class oled13:
    def __init__(self):
        # sheduler
        self.s = sched.scheduler(time.time, time.sleep)
        # OLED 1.3' display
        self.disp = SH1106.SH1106()
        # Initialize library.
        self.disp.Init()
        self.disp.clear()
        self.shd = sched.scheduler(time.time, time.sleep)
        self.image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        self.font = ImageFont.truetype('fonts/cour.ttf', 26)
        self.font10 = ImageFont.truetype('fonts/cour.ttf',12)
            
    def clock( self ):
        #print( "oled13.clock():\n")
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        now = datetime.now() # current date and time
        buf = now.strftime("%H:%M:%S")
        (sx,sy)=self.font.getsize(buf)
        draw.text( ( int((128-sx)/2), int(31-sy) ), buf, font = self.font, fill = 0)
        self.ip=getip()
        (sx,sy)=self.font10.getsize(self.ip)
        draw.text((int((128-sx)/2),64-sy), self.ip, font = self.font10, fill = 0)
        #image=image.rotate(180) 
        self.image = image
        
    def show(self):
        #print( "oled13.show():\n")
        self.disp.ShowImage(self.disp.getbuffer(self.image))    
        
    def run(self):
        #print( "oled13.run():\n")
        self.s.run()
        
    def loop(self):    
        #print( "oled13.loop():\n")
        self.s.enter(1, 1, self.loop ) 
        self.clock()
        self.show()

        
