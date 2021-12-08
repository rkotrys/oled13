#!/usr/bin/python3
import time, sys, os, io
import subprocess as proc
import threading
import logging
import Console

c=Console.Console()
kbd=Console.Kbd()
pipe = open( "/var/pipe","r",1 );

def keyhandle(name,state):
    c.prn( u'{} is {}'.format( name, state ) )

def k1(name,state):
    if state=='UP':
        c.prn( u'{} is {}'.format( name, state ) )
        c.prn( u' !!! EXIT !!!' )
        time.sleep(1)
        #c.close()
        quit()
    else:    
        c.prn( u'{} is {}'.format( name, state ) )

for k in kbd.handler.keys():
    kbd.handler[k] = keyhandle

kbd.handler['k1']=k1

def keydrv(arg):    
    while 1:
        kbd.read()
        time.sleep(0.1)
    
x = threading.Thread( name='keydrv', target=keydrv, args=(1,), daemon=True)
x.start()
str=''
#while x.isAlive():
while 1:
    if not x.isAlive(): break
    ch = pipe.read(1)
    if ch == '': 
        time.sleep(0.1)
        continue
    str = str + ch
    if len(str)==5 and str == '.END.': break
    if ch == '\n' or len(str) >= c.width:
        c.prn(str,1)
        str = ''   

c.close()   
pipe.close()    

#    for key in Console.Kbd.buttons.keys():
#        if kbd.key(key): c.prn("{:5}={}".format( key, kbd.key(key) ) )
#        time.sleep(0.02)


