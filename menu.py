#!/usr/bin/python
# -*- coding:utf-8 -*-

# /*****************************************************************************
# * | File        :	  menu.py
# * | Author      :   Robert Kotrys
# * | Function    :   Basic menu class to use with Raspberry Pi display hat
# * | Info        :   require files: 
# *----------------
# * | This version:   V1.0
# * | Date        :   2022-01-09
# * | Info        :   
# * | classes     :   menu
# ******************************************************************************/


import time, json
from PIL import Image,ImageDraw,ImageFont



class menu:
    def __init__(self,oled,font=None, size=(128,64), mode='1', bgcolor=1, color=0 ):
        """ oled is reference to display instance """
        self.oled=oled
        if font!=None:
            self.font=font
        else:
            self.font=ImageFont.truetype('fonts/cour.ttf',11)
        self.menu = [{"text":"MENU\n0","type":"t","cmd":"echo m0"},{"text":"MENU\n1","type":"t","cmd":"echo m1"},{"text":"MENU\n2","type":"t","cmd":"echo m2"}]
        self.vspace=1
        self.size=size
        self.mode=mode
        self.bgcolor=bgcolor
        self.color=color
        self.pos=0
        
    def activate(self):
        self.pos=0
        self.oled.hold=True
        self.oled.kbd.sethanddle( 'enter', self.enter_handle )
        self.oled.kbd.sethanddle( 'right', self.right_handle )
        self.oled.kbd.sethanddle( 'left', self.left_handle )
        self.oled.kbd.sethanddle( 'up', self.up_handle )
        self.oled.kbd.sethanddle( 'down', self.down_handle )
        self.show( self.drow() )
    
    def deactivate(self):
        self.oled.hold=False
        self.oled.kbd.sethanddle( 'enter', self.oled.enter_handle )
        self.oled.kbd.sethanddle( 'right', self.oled.right_handle )
        self.oled.kbd.sethanddle( 'left', self.oled.left_handle )
        self.oled.kbd.sethanddle( 'up', self.oled.up_handle )
        self.oled.kbd.sethanddle( 'down', self.oled.down_handle )
        
    
    def show(self, image):
        self.oled.image=image
        self.oled.show()
            
    def drow(self,text=None):
        """ drowinfo class - display multilnies 'content' in OLED screen """
        image = Image.new(self.mode, self.size, self.bgcolor )
        draw = ImageDraw.Draw(image)
        buf='MENU: {}'.format(self.pos+1) if text==None else 'MENU'
        (sx,sy)=draw.textsize( buf, font=self.font, spacing=self.vspace )
        header_v=sy+1
        draw.rectangle( [(0,0),(self.size[0]-1,header_v)], fill=self.color, outline=self.bgcolor, width=0 )
        draw.text( (4,0), buf, font=self.font, spacing=self.vspace, fill = self.bgcolor )
        buf = self.menu[self.pos]["text"] if text==None else text
        (sx,sy)=draw.multiline_textsize( buf, font=self.font, spacing=self.vspace )
        x=(self.size[0]-sx)//2
        y=((self.size[1]-header_v)-sy)//2
        draw.rectangle( [(0,header_v+2),(self.size[0]-1,self.size[1]-1)], fill=self.bgcolor, outline=self.color, width=1 )
        #(sx,sy)=self.font.getsize_multiline(buf, spacing=self.vspace )
        draw.multiline_text( (x,header_v+y), buf, font=self.font, spacing=self.vspace, fill = self.color )
        return image

    def enter_handle(self,name,state):
        if state=='Down':
            self.show(self.drow('[ENTER] '+self.menu[self.pos]['cmd']))
            # exec the command
            time.sleep(3)
            self.deactivate()
            time.sleep(1)
            #print( u'[MENU] enter_handle: {} is {}'.format( name, state ) )
            #print( u'exit!' )

    def right_handle(self,name,state):
        if state=='Down':
            print( u'[MENU] rght_handle: {} is {}'.format( name, state ) )    

    def left_handle(self,name,state):
        if state=='Down':
            print( u'[MENU] left_handle: {} is {}'.format( name, state ) )    
        
    def up_handle(self,name,state):
        if state=='Down':
            if self.pos  > 0:
                self.pos=self.pos-1
            self.oled.display_timeout=self.oled.display_timeout_d
            image=self.drow()
            self.oled.lock.acquire()
            self.oled.image = image
            self.oled.lock.release()
            self.oled.show()
        
    def down_handle(self,name,state):
        if state=='Down':
            if self.pos < (len(self.menu)-1):
                self.pos=self.pos+1
            self.oled.display_timeout=self.oled.display_timeout_d
            self.oled.lock.acquire()
            self.oled.image = self.drow()
            self.oled.lock.release()
            self.oled.show()
