# -*- coding:utf-8 -*-
import SH1106
import time
import config
import traceback
import subprocess as proc

import RPi.GPIO as GPIO

import time
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13

KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16



#define KEY_UP_PIN      6
#define KEY_DOWN_PIN    19
#define KEY_LEFT_PIN    5
#define KEY_RIGHT_PIN   26
#define KEY_PRESS_PIN   13
#define KEY1_PIN        21
#define KEY2_PIN        20
#define KEY3_PIN        16


# 128x64 display with hardware SPI:
disp = SH1106.SH1106()
disp.Init()

# Clear display.
disp.clear()

#init GPIO
# for P4:
# sudo vi /boot/config.txt
# gpio=6,19,5,26,13,21,20,16=pu
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

ON = 1
OFF = 0

def btn( x = 0, y = 0, state = OFF, size = 10 ):
    draw.ellipse( ( x, y, x+10, y+10 ), outline = 0, fill = state )

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.

image = Image.new('1', (disp.width, disp.height),1)
font = ImageFont.truetype('cour.ttf', 20)
font14 = ImageFont.truetype('cour.ttf', 14)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,disp.width-1,disp.height-1), outline=0, fill=1)

btystart = 10
btxstart = 110
btsize = 15
btspace = 2
btn( btxstart, btystart, ON, size = btsize )
btn( btxstart, btystart + btsize + btspace, ON, size = btsize )
btn( btxstart, btystart + (btsize + btspace)*2, ON, size = btsize  )

disp.ShowImage(disp.getbuffer(image))
# try:
refresh = 1
buttons = [ 0, 0, 0 ]
go = 1
while go:
    # with canvas(device) as draw:
    #if GPIO.input(KEY_UP_PIN): # button is released
        #draw.polygon([(20, 20), (30, 2), (40, 20)], outline=0, fill=1)  #Up
        
    #else: # button is pressed:
        #draw.polygon([(20, 20), (30, 2), (40, 20)], outline=0, fill=0)  #Up filled
        
    #if GPIO.input(KEY_LEFT_PIN): # button is released
        #draw.polygon([(0, 30), (18, 21), (18, 41)], outline=0, fill=1)  #left
    #else: # button is pressed:
        #draw.polygon([(0, 30), (18, 21), (18, 41)], outline=0, fill=0)  #left filled
        
    #if GPIO.input(KEY_RIGHT_PIN): # button is released
        #draw.polygon([(60, 30), (42, 21), (42, 41)], outline=0, fill=1) #right
    #else: # button is pressed:
        #draw.polygon([(60, 30), (42, 21), (42, 41)], outline=0, fill=0) #right filled
        
    #if GPIO.input(KEY_DOWN_PIN): # button is released
        #draw.polygon([(30, 60), (40, 42), (20, 42)], outline=0, fill=1) #down
    #else: # button is pressed:
        #draw.polygon([(30, 60), (40, 42), (20, 42)], outline=0, fill=0) #down filled
        
    #if GPIO.input(KEY_PRESS_PIN): # button is released
        #draw.rectangle((20, 22,40,40), outline=0, fill=1) #center 
    #else: # button is pressed:
        #draw.rectangle((20, 22,40,40), outline=0, fill=0) #center filled
        
    if GPIO.input(KEY1_PIN): # button is released
        if buttons[0] == 1:
            buttons[0] = 0
            btn( btxstart, btystart, ON, btsize )
            refresh = 1
    else: # button is pressed:
        if buttons[0] == 0:
            buttons[0] = 1;
            btn( btxstart, btystart, OFF, btsize )
            refresh = 1
        
    if GPIO.input(KEY2_PIN): # button is released
        if buttons[1] == 1:
            buttons[1] = 0
            btn( btxstart, btystart + btspace + btsize, ON, btsize )
            refresh = 1
    else: # button is pressed:
        if buttons[1] == 0:
            buttons[1] = 1;
            btn( btxstart, btystart + btspace + btsize, OFF, btsize )
            refresh = 1
        
    if GPIO.input(KEY3_PIN): # button is released
        if buttons[2] == 1:
            buttons[2] = 0
            btn( btxstart, btystart + (btspace + btsize) * 2, ON, btsize )
            refresh = 1
    else: # button is pressed:
        if buttons[2] == 0:
            buttons[2] = 1;
            btn( btxstart, btystart + (btspace + btsize) * 2, OFF, btsize )
            refresh = 1
        
    if not (GPIO.input(KEY3_PIN) or GPIO.input(KEY1_PIN)): # button is released
        draw.rectangle((0,0,disp.width,disp.height), outline=1, fill=1)
        draw.text((30,20), 'KONIEC', font = font, fill = 0)
        refresh = 1
        go = 0

    if refresh and buttons[0]==1:
        msg = str(proc.check_output(['vcgencmd', 'measure_temp'] ))
        draw.rectangle([1,2,100,17], fill=1, outline=1)
        draw.text((0,0), msg[7:13], font = font14, fill = 0)
    else:
        draw.rectangle([1,2,100,17], fill=1, outline=1)
        

    if refresh:
       refresh = 0
       disp.ShowImage(disp.getbuffer(image))

    time.sleep(0.1)

    
# except:
	# print("except")

GPIO.cleanup()
