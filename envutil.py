#!/usr/bin/env python2.6.6

import logging 
import sys
import time
from container_manager import containerManager
import global_varies

conf_ini = global_varies.conf_ini

def check_vm_stat():
    node_ips = []
    node_ips = conf_ini.get('node_ips')
    
    while True:
        stat = True
        succ = []
        for index, host_ip in enumerate(node_ips):
            print 'begin host_ip:%s' % host_ip
            cm = containerManager.ContainerManager(host_ip)
            ret = cm.container_manager_status()
            logging.info('host_ip:%s, result: %s' % (host_ip, str(ret)) )
            print 'host_ip:%s, result: %s' % (host_ip, str(ret))
            if ret:
                succ.append(host_ip)
            else:
                stat = False
        logging.info('start result: %s' % stat)
        print 'start result: %s' % stat
        if stat:
            logging.info('successful, please test your server interface!')
            print 'successful, please test your server interface!'
            return True
        
        for host_ip in succ:
            node_ips.remove(host_ip)
        time.sleep(3)

if __name__ == '__main__':
    pass