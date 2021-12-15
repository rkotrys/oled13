#!/usr/bin/python
# -*- coding:utf-8 -*-

import time, sched, threading
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import subprocess as proc
import SH1106
import config
import helper as h
from Kbd import Kbd

class oled13:
    def __init__(self, rpilink_address='rpi.ontime24.pl'):
        # run flag
        self.go=True
        # sheduler
        self.s = sched.scheduler(time.time, time.sleep)
        # OLED 1.3' display
        self.disp = SH1106.SH1106()
        # Keyboard 
        self.kbd=Kbd(self)
        # display state
        self.display_state=''
        self.display_timeout=10
        self.display_timeout_d=10
        # semafor
        self.lock = threading.Lock()
        # network params
        self.rpilink_address = rpilink_address
        self.isonline_flag = False
        # dev info
        self.df=h.getdevinfo()
        self.netdev=h.getnetdev()
        # Initialize library.
        self.disp.Init()
        self.disp.clear()
        # Graphix items
        self.withe = 0
        self.black = 1
        self.image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        self.font = ImageFont.truetype('fonts/cour.ttf', 26)
        self.font10 = ImageFont.truetype('fonts/cour.ttf',11)
        self.icon = ImageFont.truetype('fonts/segmdl2.ttf', 12)
        # drowinfo objects
        self.drowinfo=drowinfo(self,self.font10)
        # Set keyboard handler callback
        self.kbd.sethanddle( 'k1', self.k1_handle )
        self.kbd.sethanddle( 'k2', self.k2_handle )
        self.kbd.sethanddle( 'k3', self.k3_handle )
        self.kbd.sethanddle( 'enter', self.enter_handle )
        self.kbd.sethanddle( 'right', self.right_handle )
        

    def drowicon( self,icon=0xEC44,x=1,y=1,show=False ):
        self.lock.acquire()
        draw = ImageDraw.Draw(self.image)
        draw.text( (x,y), chr(icon), font=self.icon, fill=self.withe)     
        if show:
            self.disp.ShowImage(self.disp.getbuffer(self.image))
        self.lock.release()
            
    def clock( self ):
        #print( "oled13.clock():\n")
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        now = datetime.now() # current date and time
        buf = now.strftime("%H:%M:%S")
        (sx,sy)=self.font.getsize(buf)
        draw.text( ( int((128-sx)/2), 15 ), buf, font = self.font, fill = 0)
        self.ip=h.getip()
        (sx,sy)=self.font10.getsize(self.ip)
        draw.text((int((128-sx)/2),64-sy), self.ip, font = self.font10, fill = 0)
        draw.text((0,0), u'{:2.0f}\'C'.format(h.gettemp()), font = self.font10, fill = 0)
        #image=image.rotate(180) 
        self.lock.acquire()
        self.image = image
        self.lock.release()

    def status1( self, mode=True, drowinfo=None ):
        """ 
            status1( self, drowinfo=None, mode=True )
            drowinfo = instance of 'drowinfo' class
            mode= True (drow info and set Up Down keys handlers) |False (clear key handlers) 
        """
        if mode:
            image=drowinfo.drowinfo(h.getdevinfo(False))
            drowinfo.sethanddle()
            self.lock.acquire()
            self.image = image
            self.lock.release()
        else:
            self.drowinfo3.clearhanddle()

    def status2( self, mode=True, drowinfo=None ):
        """ 
            status2( self, drowinfo=None, mode=True )
            drowinfo = instance of 'drowinfo' class
            mode= True (drow info and set Up Down keys handlers) |False (clear key handlers) 
        """
        if mode:
            image=drowinfo.drowinfo(" status 2 ")
            drowinfo.sethanddle()
            self.lock.acquire()
            self.image = image
            self.lock.release()
        else:
            drowinfo.clearhanddle()

    def status3( self, mode=True, drowinfo=None ):
        """ 
            status3( self, drowinfo=None, mode=True )
            drowinfo = instance of 'drowinfo' class
            mode= True (drow info and set Up Down keys handlers) |False (clear key handlers) 
        """
        if mode:
            image=drowinfo.drowinfo(" status 3 ")
            drowinfo.sethanddle()
            self.lock.acquire()
            self.image = image
            self.lock.release()
        else:
            drowinfo.clearhanddle()
                
        
    def show(self):
        #print( "oled13.show():\n")
        self.lock.acquire()
        self.disp.ShowImage(self.disp.getbuffer(self.image))    
        self.lock.release()

        
    def run(self):
        #print( "oled13.run():\n")
        self.s.run()
        
    def loop(self):
        if self.go:    
            #print( "oled13.loop():\n")
            self.s.enter(1, 1, self.loop ) 
            if self.display_state=='status1':
                self.status1(True,self.drowinfo)
                if self.display_timeout > 0:
                    self.display_timeout=self.display_timeout-1
                else:
                    self.display_state=''
                    self.display_timeout=self.display_timeout_d
                self.status1(mode=False)

            if self.display_state=='status2':
                self.status2(mode=True,drowinfo=self.drowinfo)
                if self.display_timeout > 0:
                    self.display_timeout=self.display_timeout-1
                else:
                    self.display_state=''
                    self.display_timeout=self.display_timeout_d
                self.status2(mode=False)

            if self.display_state=='status3':
                self.status3(mode=True,drowinfo=self.drowinfo)
                if self.display_timeout > 0:
                    self.display_timeout=self.display_timeout-1
                else:
                    self.display_state=''
                    self.display_timeout=self.display_timeout_d
                    self.status3(mode=False)
            
            # clock() is the default    
            if self.display_state=='':         
                self.clock()
                # add online status info
                self.online_status()
                if self.isonline_flag:
                    self.drowicon(icon=0xEC3F,x=128-12,y=0)
            #self.lock.acquire()
            self.show()
            #self.lock.release()
        else:  # self.go==False
            self.disp.clear()
            self.disp.reset()
            self.disp.command(0xAE);  #--turn off oled panel
        
# system status and info
    def getdevinfo(self):
        df = {}
        with open('/proc/cpuinfo','r') as f:
            output=str(f.read()).strip().splitlines()
        for line in output:
            l=str(line).strip().split()
            if len(l)>0 and l[0]=='Serial':
                self.serial=l[2][8:]
            if len(l)>0 and l[0]=='Hardware':
                self.chip=l[2]
            if len(l)>0 and l[0]=='Revision':
                self.revision=l[2]
            if len(l)>0 and l[0]=='Model':
                self.model=str(u' '.join(l[2:])).replace('Raspberry Pi','RPi')
        with open('/boot/.id','r') as f:
            msdid=str(f.readline()).strip()
        self.msdid=msdid    
        with open('/proc/meminfo','r') as f:
            memtotal=str(f.readline()).strip().split()[1]
            memfree=str(f.readline()).strip().split()[1]
            memavaiable=str(f.readline()).strip().split()[1]
        self.memtotal= ( int(memtotal) // 1000 )    
        self.memfree= ( int(memfree) // 1000 )    
        self.memavaiable= ( int(memavaiable) // 1000 )    
        self.release=str(proc.check_output(['uname','-r'] ), encoding='utf-8').strip()
        self.machine=str(proc.check_output(['uname','-m'] ), encoding='utf-8').strip()
        buf=str(proc.check_output(['blkid','/dev/mmcblk0'] ), encoding='utf-8').strip().split()[1]
        self.puuid=buf[8:16]
        self.version='???'
        with open('/etc/os-release','r') as f:
            output=f.readlines()
        for line in output:
            l=line.split('=')
            if l[0]!='VERSION':
                continue
            else:
                self.version=str(l[1]).strip().replace('"','').replace("\n",'') 
                break   
        self.hostname=str(proc.check_output(['hostname'] ), encoding='utf-8').strip()
        essid=str(proc.check_output(['iwgetid'] ), encoding='utf-8').strip().split()[1]
        buf=str(proc.check_output(['df','-h'] ), encoding='utf-8').strip().splitlines()[1].strip().split()
        
        df['serial']=self.serial
        df['chip']=self.chip
        df['revision']=self.revision
        df['model']=self.model
        df['memtotal']=self.memtotal
        df['memfree']=self.memfree
        df['memavaiable']=self.memavaiable
        df['release']=self.release
        df['machine']=self.machine
        df['hostname']=self.hostname
        df['puuid']=self.puuid
        df['version']=self.version
        df['essid']=essid.split(':')[1].replace('"','')
        df['fs_total']=buf[1]
        df['fs_free']=buf[3]
        df['coretemp']=h.gettemp()
        df['msdid']=self.msdid
        return df

# Keyboard callbacks handlers
        
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
                self.drowinfo3.clearhanddle()
            self.display_timeout=self.display_timeout_d
        #print( u'k3_handle: {} is {}'.format( name, state ) )

    def enter_handle(self,name,state):
        if state=='Down':
            self.go=False
        print( u'enter_handle: {} is {}'.format( name, state ) )
        print( u'exit!' )

    def right_handle(self,name,state):
        if state=='Down':
            self.drowicon()
            print( u'rght_handle: {} is {}'.format( name, state ) )    
        

class drowinfo:
    def __init__(self, oled, font=None ):
        """ clock is reference to 'clock' instance """
        self.oled=oled
        if font!=None:
            self.font=font
        else:
            self.font=ImageFont.truetype('fonts/cour.ttf',11)
        self.info= []
        self.start= 0
        (sx,sy)= self.font.getsize('X')
        self.vspace=1
        self.maxly= self.oled.disp.height // int(sy+self.vspace)
        self.maxlx= self.oled.disp.width // int(sx)
        self.maxlines= 50    
        
    def sethanddle(self):
        self.oled.kbd.sethanddle( 'up', self.key_up_handler )
        self.oled.kbd.sethanddle( 'down', self.key_down_handler )

    def clearhanddle(self):
        self.oled.kbd.sethanddle( 'up', self.oled.kbd.keyhandle )
        self.oled.kbd.sethanddle( 'down', self.oled.kbd.keyhandle )
        

    def setinfo(self,content):
        self.info=[]
        if isinstance(content, list):
            for line in content:
                line=str(line)
                while len(line)>0:
                    if len(line)<=self.maxlx:
                        self.info.append(line)
                        break
                    else:
                        self.info.append(line[0:self.maxlx])
                        line=line[self.maxlx:]
        else:
            for line in content.splitlines():
                while len(line)>0:
                    if len(line)<=self.maxlx:
                        self.info.append(line)
                        break
                    else:
                        self.info.append(line[0:self.maxlx])
                        line=line[self.maxlx:]        
        
    def drowinfo(self,content=None):
        """ drowinfo class - display multilnies 'content' in OLED screen """
        if content!=None:
            self.setinfo(content)
        image = Image.new('1', (self.oled.disp.width, self.oled.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        info=""
        for i in range( self.maxly ):
            info=info+self.info[self.start+i]+"\n"
        draw.multiline_text( (1,1), info, font=self.font, spacing=self.vspace, fill = 0 )
        return image
    
    def key_up_handler(self,name,state):
        if state=='Down':
            if self.start>0:
                self.start=self.start-1
        self.oled.display_timeout=self.oled.display_timeout_d
        image=self.drowinfo()
        self.oled.lock.acquire()
        self.oled.image = image
        self.oled.lock.release()
        self.oled.show()
        
        
    def key_down_handler(self,name,state):
        if state=='Down':
            if self.start < (len(self.info)-self.maxly):
                self.start=self.start+1
        self.oled.display_timeout=self.oled.display_timeout_d
        image=self.drowinfo()
        self.oled.lock.acquire()
        self.oled.image = image
        self.oled.lock.release()
        self.oled.show()
        
        

