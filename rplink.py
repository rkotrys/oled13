#!/usr/bin/python
# -*- coding:utf-8 -*-

import time, sched, threading
from datetime import datetime
import subprocess as proc
import helper as h

class rplink:
    """ class 'rplink' xchange information and command with 'rpihub' server """
    def __init__(self, rpilink_address='rpi.ontime24.pl',rpilink_period=1):
        """ constructor """
        self.d=h.getrpiinfo()
        self.n=h.getnetdev()
        self.go=True
        self.rplink_period=rpilink_period
        self.isonline=h.online_status()
        self.rpihub=False
        


    def rpilink(self):
        """ thread """
        while self.go:
            time.sleep(self.rpilink_period)    
            if h.online_status():
                if "eth0" in self.netdev.keys():
                    ip=self.netdev['eth0'][1]
                    emac=self.netdev['eth0'][2]
                else:
                    ip='--'
                    emac='--'
                if "wlan0" in self.netdev.keys():
                    wip=self.netdev['wlan0'][1]
                    wmac=self.netdev['wlan0'][2]
                else:
                    wip='--'
                    wmac='--'
                self.d = h.getrpiinfo()
                df['ip']=ip
                df['wip']=wip
                df['emac']=emac
                df['wmac']=wmac
                df['theme']=self.cnf["global"]["theme"]
                x = requests.post( 'http://'+self.rpilink_address+'/?get=post', json=df, timeout=1)
                if x.status_code==200:
                    self.rpihub=True
                    # TODO: read respoce
                    r=json.loads(base64.standard_b64decode(x.text))
                    #print( base64.standard_b64decode(x.text) )
                    if r['status']=='OK':
                        if not self.goodtime:
                            curent_date_time=str(r['time']).split()
                            proc.run(['/bin/timedatectl', 'set-ntp', 'false' ])
                            proc.run(['/bin/timedatectl', 'set-time', curent_date_time[0] ])
                            cp=proc.run(['/bin/timedatectl', 'set-time', curent_date_time[1] ])
                            if cp.returncode==0:
                                self.goodtime=True
                        # theme
                        if r['cmd']['name']=='theme':
                            self.cnf["global"]["theme"]=r['cmd']['value']
                            clock.cnf.save()
                        # hostname    
                        if r['cmd']['name']=='hostname' and r['cmd']['sn']==self.serial:
                            new_hostname=r['cmd']['value']
                            if r['cmd']['sn']==self.serial:
                                proc.check_output(['/root/lcd144/setnewhostname.sh', new_hostname, self.hostname ] )
                                self.hostname=str(proc.check_output(['hostname'] ), encoding='utf-8').strip()
                        # reboot
                        if r['cmd']['name']=='reboot' and r['cmd']['sn']==self.serial:
                            result = proc.run(['/bin/systemctl', 'reboot'],capture_output=True, text=True);
                        # poweroff
                        if r['cmd']['name']=='poweroff' and r['cmd']['sn']==self.serial:
                            result = proc.run(['/bin/systemctl', 'poweroff'],capture_output=True, text=True);
                        # update agent software (LCD144)
                        if r['cmd']['name']=='update' and r['cmd']['sn']==self.serial:
                            result = proc.run(['/bin/git pull'], cwd='/root/'+r['cmd']['service'], shell=True, capture_output=True, text=True);
                            #print("stdout: ", result.stdout)
                            #print("stderr: ", result.stderr)
                                
                    else:
                        print( 'ERROR:' + r['status'] )    
                else:
                    self.rpihub=False
#end of rpilink()
