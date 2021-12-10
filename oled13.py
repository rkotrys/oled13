#!/usr/bin/python
# -*- coding:utf-8 -*-

import SH1106
import time, sched
import config
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
from helper import getip
from Kbd import Kbd

class oled13:
    def __init__(self):
        # sheduler
        self.s = sched.scheduler(time.time, time.sleep)
        # OLED 1.3' display
        self.disp = SH1106.SH1106()
        # Keyboard 
        self.kbd=Kbd()
        # display state
        self.display_state=''
        self.display_timeout=10
        self.display_timeout_d=10
        # Initialize library.
        self.disp.Init()
        self.disp.clear()
        self.image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        self.font = ImageFont.truetype('fonts/cour.ttf', 26)
        self.font10 = ImageFont.truetype('fonts/cour.ttf',12)
        self.icon = ImageFont.truetype('fonts/segmdl2.ttf', 12)
        self.kbd.sethanddle( 'k1', self.k1_handle )
        self.kbd.sethanddle( 'k2', self.k2_handle )
        self.kbd.sethanddle( 'k3', self.k3_handle )
            
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

    def status1( self ):
        #print( "oled13.status1():\n  0xE701 ")
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        draw.text( ( 128-12, 0 ), chr(0xE701), font = self.icon, fill = 0)
        buf = 'STATUS 1'
        (sx,sy)=self.font.getsize(buf)
        draw.text( ( int((128-sx)/2), int(31-sy) ), buf, font = self.font, fill = 0)
        buf=str(self.display_timeout)
        (sx,sy)=self.font10.getsize(buf)
        draw.text((int((128-sx)/2),64-sy), buf, font = self.font10, fill = 0)
        self.image = image

    def status2( self ):
        #print( "oled13.status2():\n")
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        buf = 'STATUS 2'
        (sx,sy)=self.font.getsize(buf)
        draw.text( ( int((128-sx)/2), int(31-sy) ), buf, font = self.font, fill = 0)
        buf=str(self.display_timeout)
        (sx,sy)=self.font10.getsize(buf)
        draw.text((int((128-sx)/2),64-sy), buf, font = self.font10, fill = 0)
        self.image = image

    def status3( self ):
        #print( "oled13.status3():\n")
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        buf = 'STATUS 3'
        (sx,sy)=self.font.getsize(buf)
        draw.text( ( int((128-sx)/2), int(31-sy) ), buf, font = self.font, fill = 0)
        buf=str(self.display_timeout)
        (sx,sy)=self.font10.getsize(buf)
        draw.text((int((128-sx)/2),64-sy), buf, font = self.font10, fill = 0)
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
        if self.display_state=='status1':
            if self.display_timeout > 0:
                self.display_timeout=self.display_timeout-1
            else:
                self.display_state=''
                self.display_timeout=self.display_timeout_d
            self.status1()

        if self.display_state=='status2':
            if self.display_timeout > 0:
                self.display_timeout=self.display_timeout-1
            else:
                self.display_state=''
                self.display_timeout=self.display_timeout_d
            self.status2()

        if self.display_state=='status3':
            if self.display_timeout > 0:
                self.display_timeout=self.display_timeout-1
            else:
                self.display_state=''
                self.display_timeout=self.display_timeout_d
            self.status3()
        
        # clock() is the default    
        if self.display_state=='':         
            self.clock()
        self.show()
        
    def k1_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status1':
                self.display_state='status1'
            else:    
                self.display_state=''
            self.display_timeout=self.display_timeout_d
        #print( u'k1_handle: {} is {}'.format( name, state ) )

    def k2_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status2':
                self.display_state='status2'
            else:    
                self.display_state=''
            self.display_timeout=self.display_timeout_d
        #print( u'k2_handle: {} is {}'.format( name, state ) )
        
    def k3_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status3':
                self.display_state='status3'
            else:    
                self.display_state=''
            self.display_timeout=self.display_timeout_d
        #print( u'k3_handle: {} is {}'.format( name, state ) )

        
