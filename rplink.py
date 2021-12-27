#!/usr/bin/python
# -*- coding:utf-8 -*-


import time, sched, threading, requests, json, base64, logging, logging.handlers
from logging.handlers import SysLogHandler
from logging import Formatter
from datetime import datetime
import subprocess as proc
import helper as h

class rplink:
    """ class 'rplink' xchange information and command with 'rpihub' server """
    def __init__(self, display, rpilink_address='rpi.ontime24.pl',rpilink_period=1, localdata={}):
        """ constructor """
        self.display=display
        self.rpilink_address=rpilink_address
        self.rplink_period=rpilink_period
        self.d=h.getrpiinfo()
        self.n=h.getnetdev()
        self.go=True
        self.isonline=h.online_status()
        self.rpihub=False
        self.goodtime=False
        self.logger = logging.getLogger(self.display)
        self.logger.setLevel( logging.DEBUG )
        self.log_handler = SysLogHandler(facility=SysLogHandler.LOG_DAEMON, address='/dev/log')
        self.log_handler.setFormatter(Formatter(fmt='[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'))
        self.logger.addHandler( self.log_handler )
        self.logger.info('[{}] rpilink logger is start!'.format(self.display))
        self.localdata=localdata
        proc.run(['/bin/timedatectl', 'set-ntp', 'false' ])
        # start
        self.x_rpilink = threading.Thread( name='rpilink', target=self.rpilink, args=(), daemon=True)
        self.x_rpilink.start()

    def setlocaldata(self,data):
        for key, val in data.items():
            self.localdata[key]=val

    def getlocaldata(self):
        return self.localdata

    def rpilink(self):
        """ thread """
        while self.go:
            time.sleep(self.rplink_period)    
            if h.online_status():
                self.d=h.getrpiinfo(self.d)
                self.n=h.getnetdev()
                self.setlocaldata( {'msdid':self.d['msdid'], 'essid':self.d['essid'], 'coretemp':self.d['coretemp'], 'memavaiable':self.d['memavaiable']} )
                #self.d['theme']= json.dumps({ 'display':self.display, 'localdata':self.localdata }) 
                self.d['theme']=base64.standard_b64encode( bytes( json.dumps({ 'display':self.display, 'localdata':self.localdata }), 'utf-8' ) )
                #df['theme']=self.cnf["global"]["theme"]
                address_str = 'http://'+self.rpilink_address+'/?get=post'
                try:
                    x = requests.post( address_str, json=self.d, timeout=1)
                except requests.exceptions.RequestException as e:
                    self.logger.info( '[{}] post connection to {} fail'.format(self.display,self.rpilink_address) )
                    continue
                
                self.logger.debug( '[{}] post connection to {} has status code {}'.format(self.display,self.rpilink_address,x.status_code) )
                if x.status_code==200:
                    self.rpihub=True
                    # read respoce
                    r=json.loads(base64.standard_b64decode(x.text))
                    #print( base64.standard_b64decode(x.text) )
                    if r['status']=='OK':
                        if not self.goodtime:
                            now=datetime.now()
                            date=now.strftime("%Y-%m-%d")
                            curent_date_time=str(r['time']).split()
                            if curent_date_time[0]!=date:
                                proc.run(['/bin/timedatectl', 'set-time', curent_date_time[0] ])
                            cp=proc.run(['/bin/timedatectl', 'set-time', curent_date_time[1] ])
                            if cp.returncode==0:
                                self.goodtime=True
                        # theme
                        #if r['cmd']['name']=='theme':
                        #    self.cnf["global"]["theme"]=r['cmd']['value']
                        #    clock.cnf.save()
                        #
                        # hostname    
                        if r['cmd']['name']=='hostname' and r['cmd']['sn']==self.d['serial']:
                            h.hostname(r['cmd']['value'])
                        # reboot
                        if r['cmd']['name']=='reboot' and r['cmd']['sn']==self.d['serial']:
                            result = proc.run(['/bin/systemctl', 'reboot'],capture_output=True, text=True);
                        # poweroff
                        if r['cmd']['name']=='poweroff' and r['cmd']['sn']==self.d['serial']:
                            result = proc.run(['/bin/systemctl', 'poweroff'],capture_output=True, text=True);
                        # update agent software <LCD144,|oled13>
                        if r['cmd']['name']=='update' and r['cmd']['sn']==self.d['serial']:
                            result = proc.run(['/bin/git pull'], cwd='/root/'+r['cmd']['service'], shell=True, capture_output=True, text=True);
                            #print("stdout: ", result.stdout)
                            #print("stderr: ", result.stderr)
                                
                    else:
                        print( 'ERROR:' + r['status'] )    
                else:
                    self.rpihub=False
            else:
                print("rplink Of-line")        
        else:
            self.x_rpilink.stop() 
                       
#end of rpilink()
