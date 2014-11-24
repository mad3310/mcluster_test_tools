#coding:gbk

import os
import global_varies

log = global_varies.log
conf_ini = global_varies.conf_ini

def install_vagrant():
    pass

def install_virtualBox():
    pass


class VagrantCluster():
    """
    vagrant cluster operations
    """

    def __init__(self):
        """Constructor"""
        pass

    def rewrite_vagrantfile(self, vagrantfile_path):
        base_vagrantfile_dir = conf_ini.get('path').get('base_vagrantfile_dir')
        node_num = conf_ini.get('Vagrantfile').get('node_num')
        vm_name = conf_ini.get('Vagrantfile').get('vm_name')
        box_name = conf_ini.get('Vagrantfile').get('box_name')
        f = open(base_vagrantfile_dir, 'r')
        content = f.read()
        f.close()
        num_str = 'SERVER_NUM = %s' % node_num
        box_str = 'box = "%s"' % box_name
        #new_cont = content.replace('SERVER_NUM = 2', num_str).replace('vm-cluster-node', vm_name).replace('box = "init"', box_str)
        new_cont = content.replace('SERVER_NUM = 2', num_str).replace('vm-cluster-node', vm_name)
        f = open(vagrantfile_path, 'w')
        f.write(new_cont)
        f.close()
    
    def create(self):
        vagrant_dir = conf_ini.get('path').get('vagrant_dir')
        base_box_dir = conf_ini.get('path').get('base_box_dir')
        box_name = conf_ini.get('Vagrantfile').get('box_name')
        if not os.path.exists(vagrant_dir):
            log.debug('创建工作目录 %s' % vagrant_dir)
            os.system('mkdir "%s" ' % vagrant_dir)
        base_box_name = os.path.basename(base_box_dir)
        dest_path = os.path.join(vagrant_dir, base_box_name)
        
        mount_file = conf_ini.get('path').get('mount_file')
        log.info('拷贝deploy.sh文件：从 %s 拷贝至 %s' % (mount_file, vagrant_dir) )
        os.system('copy "%s" "%s" ' % (mount_file, vagrant_dir) )
        
        #log.info('拷贝box文件：从 %s 拷贝至 %s' % (base_box_name, dest_path) )
        #os.system('copy "%s" "%s" ' % (base_box_dir, dest_path) )
        log.debug('进入工作目录 ：%s' % vagrant_dir)
        os.chdir(vagrant_dir)
        #log.info('添加box，执行：vagrant box add %s %s' % (box_name, base_box_name) )
        #os.system('vagrant box add %s %s' % (box_name, base_box_name) )
        log.info('初始化vagrant, 执行： vagrant init %s' % box_name)
        os.system('vagrant init %s' % box_name)
        vagrantfile_path = os.path.join(vagrant_dir, 'Vagrantfile')
        log.info('重新编写Vagrantfile')
        self.rewrite_vagrantfile(vagrantfile_path)
        os.chdir(vagrant_dir)
        log.info('启动vagrant集群服务器')
        os.system('vagrant up')
        
    def do(self, action):
        vagrant_dir = conf_ini.get('path').get('vagrant_dir')
        os.chdir(vagrant_dir)
        log.info('do action: %s ,  %s' % (action, os.path.basename(vagrant_dir)))
        os.system(r'vagrant %s' % action)
    
    def up(self):
        self.do('up')
    
    def halt(self):
        self.do('halt')
    
    def destroy(self):
        self.do('destroy')
    
    def suspend(self):
        self.do('suspend')
    
    def reload(self):
        self.do('reload')