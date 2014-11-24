
import pexpect
import commands
import time

class ContainerManager():
    
    def __init__(self, host_ip):
        self.timeout = 4
        self.host_ip = host_ip

    def connect_vm(self):
        ssh = pexpect.spawn(r"ssh -p 22 root@%s" % self.host_ip)
        index = ssh.expect(["password", 'continue connecting (yes/no)?', pexpect.EOF, pexpect.TIMEOUT], timeout=self.timeout)
        if index == 0:
            ssh.sendline('vagrant\n')
        elif index == 1:
            ssh.sendline('yes\n')
            ssh.expect('password:')
            ssh.sendline('vagrant\n')
        else:
            ssh = False
        return ssh

    def get_vm_stat(self):
        stat = True
        con = self.connect_vm()
        if not con:
            stat = False
        return stat

    def get_cm_stat(self):
        stat = True
        ssh = self.connect_vm()
        if not ssh:
            stat = False
        else:
            ssh.sendline("curl -d 'zkAddress=127.0.0.1' 'http://%s:8888/admin/conf'\n" % self.host_ip)
            index = ssh.expect(["successful", pexpect.EOF, pexpect.TIMEOUT], timeout=self.timeout)
            if index != 0:
                stat = False
                ssh.close()
        return stat

    def start_cm(self):
        stat = self.get_cm_stat()
        print stat ,111
        if not stat:
            vm_stat = self.get_vm_stat()
            if not vm_stat:
                return
            ssh = self.connect_vm()
            ssh.sendline("/vagrant/deploy.sh\n")
            start_index = ssh.expect(["END", pexpect.EOF, pexpect.TIMEOUT], timeout=40)
            print start_index, 444
            ssh.close()

    def container_manager_status(self):
        self.start_cm()
        print 'wait 1 seconds...'
        time.sleep(1)
        if self.get_cm_stat():
            return True
        return False

if __name__ == '__main__':
    c = ContainerManager('192.168.33.121')
    print c.container_manager_status()