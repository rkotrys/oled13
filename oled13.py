#!/usr/bin/python
# -*- coding:utf-8 -*-

# /*****************************************************************************
# * | File        :	  oled13.py
# * | Author      :   Robert Kotrys
# * | Function    :   Basic class to use with Raspberry Pi 128x64 1.3' mono oled hat
# * | Info        :   require files: SH1106.py, config.py, Kbd.py, helper.py,
# * |             :   rplink.py, menu.py
# *----------------
# * | This version:   V1.0
# * | Date        :   2022-01-09
# * | Info        :   include 'oled13' run file and 'oled13.service'
# * | classes     :   oled13, menu, drowinfo
# ******************************************************************************/


import time, sched, threading, sys, signal, json
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import subprocess as proc
import SH1106
import config
import helper as h
from Kbd import Kbd
from rplink import rplink
from menu import menu

class oled13:
    def __init__(self, rpilink_address='rpi.ontime24.pl'):
        # run flag
        self.go=True
        self.hold=False
        # sheduler
        self.s = sched.scheduler(time.time, time.sleep)
        # OLED 1.3' display driver
        self.disp = SH1106.SH1106()
        # Keyboard driver
        self.kbd=Kbd(self)
        # rpilink object
        self.rpilink=rplink(display='oled13', rpilink_address=rpilink_address, rpilink_period=2)
        self.rpilink.setlocaldata( {'theme':'mono'} )
        # menu object
        self.menu=menu(self, font=None, size=(self.disp.width,self.disp.height), mode='1', bgcolor=1, color=0)
        self.menu.setmenu([{"text":"MENU 1","type":"t","cmd":"echo m1"},{"text":"MENU 2\nline 2\nline 3","type":"t","cmd":"echo m2"},{"text":"MENU 3","type":"t","cmd":"echo m3"}])
        # display state
        self.display_state=''
        self.display_timeout=15
        self.display_timeout_d=15
        # semafor for save 'image' modifications
        self.lock = threading.Lock()
        # network params
        self.rpilink_address = rpilink_address
        self.isonline_flag = False
        # dev info
        self.df=h.getrpiinfo()
        self.netdev=h.getnetdev()
        self.rpilink.setlocaldata( { 'msdid':self.df['msdid'], 'essid':self.df['essid'], 'coretemp':self.df['coretemp'], 'memavaiable':self.df['memavaiable'],'netdev':self.netdev} )
        # Initialize and clean the display.
        self.disp.Init()
        self.disp.clear()
        # Graphix items
        self.withe = 0
        self.black = 1
        self.image = None #Image.new('1', (self.disp.width, self.disp.height), "WHITE")
        self.font = ImageFont.truetype('fonts/cour.ttf', 26)
        self.font10 = ImageFont.truetype('fonts/cour.ttf',11)
        self.icon = ImageFont.truetype('fonts/segmdl2.ttf', 12)
        self.symbols = {'bt':0xE702,'econnect':0xE839,'wconnect':0xEC3F,'ewconnect':0xEE77,'glob':0xE12B,'htransfer':0xE8AB,'hbtransfer':0xF1CC,'vtransfer':0xE8CB,'ap':0xEC50,'temp':0xE9CA,'off':0xEA39}
        # drowinfo objects
        self.drowinfo=drowinfo(self,self.font10)
        # Set keyboard handler callback
        self.kbd.sethanddle( 'k1', self.k1_handle )
        self.kbd.sethanddle( 'k2', self.k2_handle )
        self.kbd.sethanddle( 'k3', self.k3_handle )
        self.kbd.sethanddle( 'enter', self.enter_handle )
        self.kbd.sethanddle( 'right', self.right_handle )
        self.kbd.sethanddle( 'left', self.left_handle )
        self.kbd.sethanddle( 'up', self.up_handle )
        self.kbd.sethanddle( 'down', self.down_handle )
        

    def drowicon( self, icon, pos, show=False ):
        t=u''
        if isinstance(icon, list):
            lst=True
            for c in icon: t+=chr(c)
        else:
            t=chr(icon)
        self.lock.acquire()
        draw = ImageDraw.Draw(self.image)
        draw.text( pos, t, font=self.icon, fill=self.withe)     
        if show:
            self.disp.ShowImage(self.disp.getbuffer(self.image))
        self.lock.release()
            
    def clock( self ):
        """ drow clock face, style: digital """
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

    def status( self, content=" - Status -", drowinfo=None ):
        """ 
            status( self, content=" ", drowinfo=None, mode=True )
            content = list of str or multiline text to display
            drowinfo = instance of 'drowinfo' class
        """
        if self.display_timeout==self.display_timeout_d:
            self.kbd.sethanddle( 'up', drowinfo.key_up_handler )
            self.kbd.sethanddle( 'down', drowinfo.key_down_handler )
        if self.display_timeout==0:
            self.kbd.sethanddle( 'up', self.up_handle )
            self.kbd.sethanddle( 'down', self.down_handle )
        image=drowinfo.drow(content)
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
        if self.go :
            self.s.enter(1, 1, self.loop ) 
            if not self.hold:    
                #print( "oled13.loop():\n")
                if self.display_state in ['status1', 'status2', 'status3']:
                    if self.display_state=='status1':
                        content=h.rpiinfo_str( self.rpilink.d )
                    if self.display_state=='status2':
                        wlans_str=u'[{}] WLANs\n'.format(len( self.rpilink.scan ))
                        if len(self.rpilink.scan)>0:
                            for it in self.rpilink.scan.keys():
                                wlans_str += u'{} [{}]\n'.format( self.rpilink.scan[it]['name'], self.rpilink.scan[it]['level'] )
                        else:
                            wlans_str += 'WLANS not found!'    
                        content=wlans_str
                    if self.display_state=='status3':
                        content="K3 Status"
                    self.status(drowinfo=self.drowinfo, content=content )    
                    if self.display_timeout > 0:
                        self.display_timeout=self.display_timeout-1
                    else:
                        self.display_state=''
                        self.display_timeout=self.display_timeout_d
                # clock() is the default    
                if self.display_state=='':         
                    self.clock()
                    # add online status info
                    if self.rpilink.isonline:
                        icon=self.symbols['off']
                        if len(self.df['ip'])>2 and len(self.df['wip'])>2: 
                            icon=self.symbols['ewconnect']
                        else:
                            if len(self.df['ip'])>2 and len(self.df['wip'])==2:
                                icon=self.symbols['econnect']
                            if len(self.df['ip'])==2 and len(self.df['wip'])>2:
                                icon=self.symbols['wconnect']
                        ic=[icon]
                        #ic.insert(0,self.symbols['bt'])               
                        self.drowicon( icon=ic, pos=(128-12*len(ic),0) )
                self.show()
            else:
                if self.display_timeout > 0:
                    self.display_timeout=self.display_timeout-1
                else:
                    self.display_state=''
                    self.display_timeout=self.display_timeout_d
                    self.menu.deactivate()
                    
        else:  # self.go==False
            self.disp.clear()
            self.disp.reset()
            self.disp.command(0xAE);  #--turn off oled panel

# Keyboard callbacks handlers
        
    def k1_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status1':
                self.display_state='status1'
            else:    
                self.display_state=''
                self.kbd.sethanddle( 'up', self.kbd.keyhandle )
                self.kbd.sethanddle( 'down', self.kbd.keyhandle )
            self.display_timeout=self.display_timeout_d
        #print( u'k1_handle: {} is {}'.format( name, state ) )

    def k2_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status2':
                self.display_state='status2'
            else:    
                self.display_state=''
                self.kbd.sethanddle( 'up', self.kbd.keyhandle )
                self.kbd.sethanddle( 'down', self.kbd.keyhandle )
            self.display_timeout=self.display_timeout_d
        #print( u'k2_handle: {} is {}'.format( name, state ) )
        
    def k3_handle(self,name,state):
        if state=='Down':
            if self.display_state!='status3':
                self.display_state='status3'
            else:    
                self.display_state=''
                self.kbd.sethanddle( 'up', self.kbd.keyhandle )
                self.kbd.sethanddle( 'down', self.kbd.keyhandle )
            self.display_timeout=self.display_timeout_d
        #print( u'k3_handle: {} is {}'.format( name, state ) )

    def enter_handle(self,name,state):
        if state=='Down':
            # self.go=False
            # print( u'enter_handle: {} is {}'.format( name, state ) )
            self.menu.activate()
            # print( u'exit!' )

    def right_handle(self,name,state):
        if state=='Down':
            print( u'rght_handle: {} is {}'.format( name, state ) )    

    def left_handle(self,name,state):
        if state=='Down':
            print( u'left_handle: {} is {}'.format( name, state ) )    

    def up_handle(self,name,state):
        if state=='Down':
            print( u'up_handle: {} is {}'.format( name, state ) )    

    def down_handle(self,name,state):
        if state=='Down':
            print( u'down_handle: {} is {}'.format( name, state ) )    
        

class drowinfo:
    def __init__(self, oled, font=None ):
        """ oled is reference to 'oled13' instance """
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
        
    def drow(self,content=None):
        """ drowinfo class - display multilnies 'content' in OLED screen """
        if content!=None:
            self.setinfo(content)
        image = Image.new('1', (self.oled.disp.width, self.oled.disp.height), "WHITE")
        draw = ImageDraw.Draw(image)
        info=""
        for i in range( self.maxly ):
            if (self.start+i) < len(self.info):
                info=info+self.info[self.start+i]+"\n"
        draw.multiline_text( (1,1), info, font=self.font, spacing=self.vspace, fill = 0 )
        return image
    
    def key_up_handler(self,name,state):
        if state=='Down':
            if self.start>0:
                self.start=self.start-1
        self.oled.display_timeout=self.oled.display_timeout_d
        image=self.drow()
        self.oled.lock.acquire()
        self.oled.image = image
        self.oled.lock.release()
#        self.oled.show()
        
        
    def key_down_handler(self,name,state):
        if state=='Down':
            if self.start < (len(self.info)-self.maxly):
                self.start=self.start+1
        self.oled.display_timeout=self.oled.display_timeout_d
        image=self.drow()
        self.oled.lock.acquire()
        self.oled.image = image
        self.oled.lock.release()
 #       self.oled.show()
        
oled=None
def main():
    global oled
    link_address=sys.argv[1] if len(sys.argv)>1 else 'rpi.ontime24.pl'
    try:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGHUP, sighup_handler)
        oled = oled13(rpilink_address=link_address)
        oled.loop()
        oled.run()
        while oled.go:
            time.sleep(1)
        oled.disp.clear()
        oled.disp.reset()
        oled.disp.command(0xAE);  #--turn off oled panel
        sys.exit(0)
        
    except IOError as e:
        print(e)
        
    except KeyboardInterrupt:    
    #    config.module_exit()
        oled.disp.clear()
        oled.disp.reset()
        oled.disp.command(0xAE);  #--turn off oled panel
        exit()    

def sigint_handler(signum, frame):
    global oled
    oled.rpilink.logger.debug( u'[{}] exit by SIGINT'.format(oled.rpilink.display) )
    oled.go=False
    oled.disp.clear()
    time.sleep(3)
    sys.exit( 0 )    

def sigterm_handler(signum, frame):
    global oled
    oled.rpilink.logger.debug( u'[{}] exit by SIGTERM'.format(oled.rpilink.display) )
    oled.go=False
    oled.disp.clear()
    time.sleep(3) 
    sys.exit( 0 )    

def sighup_handler(signum, frame):
    global oled
    oled.rpilink.logger.debug( u'[{}] get SIGHUP'.format(oled.rpilink.display) )

if __name__ == "__main__":
    main()
        

