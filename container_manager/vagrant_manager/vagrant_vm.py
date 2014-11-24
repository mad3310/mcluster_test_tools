#coding:gbk

import os
import global_varies

from vagrant_cluster import VagrantCluster

log = global_varies.log
conf_ini = global_varies.conf_ini

class Vagrant(VagrantCluster):
    
    def __init__(self):
        pass

    def do(self, action):
        vip_path = conf_ini.get('path').get('vip_path')
        os.chdir(vip_path)
        log.info('do vagrant %s' % action)
        os.system('vagrant %s' % action)

    def create(self):
        pass