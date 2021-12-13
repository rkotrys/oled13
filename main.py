#!/usr/bin/python
# -*- coding:utf-8 -*-

import time   #, subprocess, sched
from oled13 import oled13

try:
    oled = oled13()
    oled.loop()
    oled.run()
    while oled.go:
        time.sleep(10)
    exit()
    
except IOError as e:
    print(e)
    
except KeyboardInterrupt:    
#    config.module_exit()
    oled.disp.clear()
    oled.disp.reset()
    oled.disp.command(0xAE);  #--turn off oled panel
    exit()
