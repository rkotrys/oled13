#!/usr/bin/python3
import time, sys, os, io
import subprocess as proc
import Console, Kbd

pipe = '/var/pipe'

c=Console.Console(logoname='KR_logo_128x66_1b_r.bmp')
k=Kbd.Kbd()

def hk1(name,state):
    if state=='UP':
        c.clrdisp()
        c.prn( u' !!! EXIT !!!' )
        time.sleep(1)
        c.clrdisp()
        quit()

def hk2(name,state):
    # MAC
    if state=='UP':
        msg = proc.check_output(["./showip", "wlan0"], encoding='utf-8' )
        c.prn( msg )
        #c.prn( str( msg, encoding='utf-8' ) )

def hk3(name,state):
    # TEMP
    if state=='UP':
        r = proc.run(["./showtemp"], capture_output=True, encoding='utf-8' )
        #c.prn( str(r.stdout, encoding='utf-8' ) )
        c.prn( r.stdout )

def prnl( msg ):
    f = open(pipe,'w')
    f.write( msg+"\n" )
    f.close()

k.sethanddle('k1',hk1)
k.sethanddle('k2',hk2)
k.sethanddle('k3',hk3)

while c.x.isAlive():
   time.sleep(1)
   msg = proc.check_output(["./showip", "wlan0"], encoding='utf-8' )
   if msg != '':
       c.drowicon(0xEC3F, 112, -1 )
   
c.close()   


