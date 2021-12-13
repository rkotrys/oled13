#!/usr/bin/python
# -*- coding:utf-8 -*-

import time, sched, threading
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import subprocess as proc
import SH1106
import config
from helper import getip
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
        self.df=self.getdevinfo()
        self.netdev=self.getnetdev()
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
        self.ip=getip()
        (sx,sy)=self.font10.getsize(self.ip)
        draw.text((int((128-sx)/2),64-sy), self.ip, font = self.font10, fill = 0)
        draw.text((0,0), '['+self.df['essid']+']', font = self.font10, fill = 0)
        #image=image.rotate(180) 
        self.lock.acquire()
        self.image = image
        self.lock.release()

    def status1( self ):
        #print( "oled13.status1():\n  0xE701 ")
        self.df=self.getdevinfo()
        buf=str(proc.check_output(['df','-h'] ), encoding='utf-8').strip().splitlines()[1].strip().split()
        info = u'HOST: ' + self.df['hostname'] + u"\nSN: " + self.df['serial'] + u"\nPUUID: " + self.df['puuid'] + u"\nCore: " + self.df['release'] + u'\nVer: ' + self.df['version']
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        draw.multiline_text( (1,1), info, font=self.font10, spacing=1, fill = 0 )
        self.lock.acquire()
        self.image = image
        self.lock.release()

    def status2( self ):
        #print( "oled13.status2():\n")
        self.df=self.getdevinfo()
        buf=str(proc.check_output(['df','-h'] ), encoding='utf-8').strip().splitlines()[1].strip().split()
        info = self.df['model']
        info = info + u'\nC:' + self.df['chip'] + u' ' + self.df['machine']
        info = info + u'\nFS: ' + u'{}, fr {}'.format( self.df['fs_total'], self.df['fs_free'])
        info = info + u'\nRAM {:3.1f}G, fr {:3.1}G'.format(float(self.df['memtotal']),float(self.df['memavaiable']))
        image = Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        draw.multiline_text( (1,1), info, font=self.font10, spacing=1, fill = 0 )
        self.lock.acquire()
        self.image = image
        self.lock.release()

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
        self.lock.acquire()
        self.image = image
        self.lock.release()
        
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
                # add online status info
                self.online_status()
                if self.isonline_flag:
                    self.drowicon(icon=0xEC3F,x=128-12,y=0)
            self.show()
        else:  # self.go==False
            self.disp.clear()
            self.disp.reset()
            self.disp.command(0xAE);  #--turn off oled panel

    # online status
    def online_status(self):
        try:
            r = str(proc.check_output(['/bin/ping', '-4', '-c', '3', '-i', '0', '-f', '-q', self.rpilink_address] ), encoding='utf-8').strip()
        except proc.CalledProcessError:
            r = '0 received'
        ind = int(r.find(' received'))
        if( int(r[ind-1:ind]) > 0 ):
            self.isonline_flag = True
        else:
            self.isonline_flag = False        
        
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
        with open('/proc/meminfo','r') as f:
            memtotal=str(f.readline()).strip().split()[1]
            memfree=str(f.readline()).strip().split()[1]
            memavaiable=str(f.readline()).strip().split()[1]
        self.memtotal= ( float(memtotal) / 1000000.0 )    
        self.memfree= ( float(memfree) / 1000000.0 )    
        self.memavaiable= ( float(memavaiable) / 1000000.0 )    
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
        return df

    def getnetdev(self):
        netdev={}
        with open('/proc/net/dev','r') as f:
            dev = f.read()
            for devname in ['eth0', 'eth1', 'wlan0', 'wlan1']:
                if dev.find(devname) > -1:
                    buf = str(proc.check_output([ 'ip', '-4', 'address', 'show', 'dev', devname ]), encoding='utf-8')
                    if len(buf)>1: 
                        ip=buf.strip().splitlines()[1].split()[1]
                    else:
                        ip='--'
                    mac=str(proc.check_output([ 'ip', 'link', 'show', 'dev', devname ]), encoding='utf-8').strip().splitlines()[1].split()[1]
                    netdev[devname]=(devname,ip,mac)
        return netdev            

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
        
