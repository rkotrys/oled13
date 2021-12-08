#!/usr/bin/python3
import time, sys, os, io
import subprocess as proc
import Kbd

pipe = '/var/pipe'

def prnl( msg ):
    f = open(pipe,'w')
    f.write( msg+"\n" )
    f.close()
    
def hk1( name, state ):
    if state=='Down' and Kbd.Kbd.buttons['enter']==1: 
        prnl("Keyboard EXIT!")
        sys.exit(1)
    prnl( u'{} is {}'.format( name, state ) )

def hk2( name, state ):
    prnl( u'{} is {}'.format( name, state ) )

def hk3( name, state ):
    prnl( u'{} is {}'.format( name, state ) )

def henter( name, state ):
    if state=='Down' and Kbd.Kbd.buttons['k1']==1: 
        prnl("Keyboard EXIT!")
        sys.exit(1)
    prnl( u'{} is {}'.format( name, state ) )
 
kbd=Kbd.Kbd()
kbd.sethanddle( 'k1', hk1 )
kbd.sethanddle( 'k2', hk2 )
kbd.sethanddle( 'k3', hk3 )
kbd.sethanddle( 'enter', henter )

while kbd.x.isAlive():
   time.sleep( 1 )
