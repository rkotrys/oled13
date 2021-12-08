# -*- coding:utf-8 -*-
import SH1106
import time, datetime, config, traceback
import threading
import subprocess as proc
import RPi.GPIO as GPIO

from PIL import Image, ImageDraw, ImageFont

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

ON = 0
OFF = 1

class Console:    
    x=0
    y=0
    
    def __init__( self, logoname='KR_logo_128x66_1b_r.bmp', mode='1', fname='cour.ttf', fsize=11, iconsize=16 ):
        # 128x64 display with hardware SPI:
        self.disp = SH1106.SH1106()
        self.disp.Init()
        self.disp.clear()    # Clear display.
        self.dsize = (self.disp.width, self.disp.height)
        self.dmode = mode
        self.fname = fname
        self.fsize = fsize
        self.black = 1
        self.withe = 0
        self.dfill = self.withe
        self.image = Image.new( self.dmode, (self.disp.width, self.disp.height), self.black )
        self.font = ImageFont.truetype(self.fname, self.fsize)
        self.icon = ImageFont.truetype('segmdl2.ttf', iconsize)
        self.fontsize = self.font.getsize(u'R');
        self.width = int( (self.dsize[0]) / self.fontsize[0])
        self.height = int(self.dsize[1] / self.fontsize[1])
        self.drow = ImageDraw.Draw(self.image)
        self.lock = threading.Lock()
        # frame
        #self.drow.rectangle((0,0,self.dsize[0]-11,self.dsize[1]-1), outline=self.withe, fill=self.black)
        self.buf = []
        for n in range(0,self.height):
            self.buf.append( u' '*self.width ); 
        #Console.showbuf(self)
        #self.showlogo(logoname)
        self.clrdisp()
        #self.drowicon(0xEC44, 112, -1 )
        #self.drowicon(0xEC3F, 112, -1 )
        #self.drowicon(0xEC41, 112, 16 )
        #time.sleep(1.0)
        self.pipe = open( "/var/pipe","r",1 );
        self.x = threading.Thread( name='console', target=self.listen, args=(0.1,), daemon=True)
        self.x.start()

        
    def showlogo(self,fname):
        Himage2 = Image.new('1', (self.disp.width, self.disp.height), 0)  # 0: clear the frame
        bmp = Image.open(fname)
        Himage2.paste(bmp, (0,5))
        #Himage2=Himage2.rotate(180)
        self.lock.acquire() 	
        self.disp.ShowImage(self.disp.getbuffer(Himage2))
        self.lock.release()
    

    def prn(self,text, newline=1):
        #print(text)
        lines = text.splitlines()
        for line in lines:
            n = 0
            #print(line)
            if lines.index(line)!=0:
                Console.x = 0
                if Console.y < self.height-1:
                    Console.y += 1                    
                else:
                    for l in range(0,self.height-1):
                        self.buf[l] = self.buf[l+1]
                    self.buf[self.height-1] = " "*self.width    
            while n<(len(line)):
                #print("x:{:3}, y:{:3}, n:{:3}, ->{}".format(Console.x, Console.y, n, line[n]) )
                if Console.x == self.width-1:
                    self.buf[Console.y] = self.buf[Console.y][0:Console.x] + line[n]
                    Console.x = 0
                    if Console.y < self.height-1:
                        Console.y += 1
                    else:
                        for l in range(0,self.height-1):
                            self.buf[l] = self.buf[l+1]
                        self.buf[self.height-1] = " "*self.width    
                else:
                    self.buf[Console.y] = self.buf[Console.y][0:Console.x] + line[n] + self.buf[Console.y][(Console.x+1):(self.width-1)]                
                    Console.x += 1
                n += 1   
        if newline:
            Console.x = 0
            if Console.y < self.height-1:
                Console.y += 1                    
            else:
                for l in range(0,self.height-1):
                    self.buf[l] = self.buf[l+1]
                self.buf[self.height-1] = " "*self.width    
    
        self.showbuf()


    def out(self,text,w=0,c=0):
        if ( (len(text)+c) > self.width ):
            text = str( text[0:(16-c)] )
        fh = self.fontsize[1]+1
        fw = self.fontsize[0]
        self.lock.acquire()
        self.drow.rectangle( ( c * fw, w * fh+1, 
                             ( c+len(text) ) * self.fontsize[0], (w+1) * fh ), 
                             outline=self.black, fill=self.black )
        self.drow.text( (c*fw,w*fh), text, font=self.font, fill=self.withe)
        self.disp.ShowImage(self.disp.getbuffer(self.image))
        self.lock.release()
    
    def drowicon( self,icon=0xEC44,x=1,y=1 ):
        self.lock.acquire()
        self.drow.text( (x,y), chr(icon), font=self.icon, fill=self.withe)     
        self.disp.ShowImage(self.disp.getbuffer(self.image))
        self.lock.release()

    def showbuf(self):
        self.lock.acquire()
        self.drow.rectangle( ( 0,0,self.width*self.fontsize[0],self.height*self.fontsize[1]+1, ), outline=self.black, fill=self.black )
        for row in range(0,self.height):
            self.drow.text( (0,row*self.fontsize[1]), self.buf[row], font=self.font, fill=self.withe)
            
        self.disp.ShowImage(self.disp.getbuffer(self.image))  
        self.lock.release()        
        
    def clrdisp(self):
        self.lock.acquire()
        self.drow.rectangle( (0, 0, self.dsize[0], self.dsize[1] ), outline=self.black, fill=self.black )
        self.disp.ShowImage(self.disp.getbuffer(self.image)) 
        self.lock.release()        

    def clrbuf(self):
        for n in range(0,self.height):
            self.buf[n] = u' '*self.width

    def info(self):
        l=0
        self.out( u'{:^17}'.format(time.strftime("%X")),0 )
        msg = str(proc.check_output(['hostname'] ), encoding='utf-8')
        self.out( u'host: {}'.format(msg.strip()),1 )
        msg = str(proc.check_output(['./showip', 'br0'] ), encoding='utf-8')
        self.out( msg.strip(), 2 )
        #msg = str(proc.check_output(['./showip', 'wlan0'] ), encoding='utf-8')
        #self.out( u'{}'.format(msg.strip()),3 )
        msg = str(proc.check_output(['vcgencmd', 'measure_temp'] ), encoding='utf-8')
        self.out( msg.strip(),4)
    
    def getImage(self):
        return self.image

    def refresh(self):
        Console.showbuf(self)
        #self.disp.ShowImage(self.disp.getbuffer(self.image)) 

    def close(self):
        self.pipe.close()
        Console.clrdisp(self)
        GPIO.cleanup()   

    def listen(self, period):
        st=''
        while 1:
            #if not x.isAlive(): break
            ch = self.pipe.read(1)
            if ch == '': 
                time.sleep(period)
                continue
            st = st + ch
            if len(st)==5 and st == '.END.': break
            if ch == '\n' or len(st) >= self.width:
                self.prn(st,1)
                st = ''   
    

