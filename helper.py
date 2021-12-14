#!/usr/bin/python
# -*- coding:utf-8 -*-

import subprocess

def getip():
    """ get a first IP v.4 address """
    ip="- no IP -"
    for dev in ('eth0','wlan0'):
        w=str( subprocess.run(["ip -4 a l "+dev+"|grep inet"], shell=True, capture_output=True, text=True ).stdout ).split()
        if( len(w)>1 ):
            ip = w[1]
            break
    return ip            

def gettemp():
    """ get the core temperature and return as float in 'C """
    with open('/sys/class/thermal/thermal_zone0/temp', "r") as file:
        tmp = float(file.read(5))/1000
    return tmp    