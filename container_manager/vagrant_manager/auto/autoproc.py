#coding:gbk
"""
�����Զ�������
"""
import autoutil
import copy
import traceback
import subprocess, sys
import win32api, win32con, win32process
import psutil

def getProcessNamesByPsutil():
    pnames = []
    plist = psutil.get_process_list()
    for p in plist:
        pnames.append(p.name.lower())
    return pnames

#��������
def createProcess(cmd, wait = False):
    if wait:
        proc = autoutil.tryExcept(subprocess.Popen, cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    else:
        proc = autoutil.tryExcept(subprocess.Popen, cmd)
    if autoutil.isExcept(proc):
        print cmd
        print 'createProcess �����쳣: %s' % str(traceback.format_exc())
        return
    if not wait:
        return proc.pid
    proc.communicate()

#�ж�ָ��id�Ľ����Ƿ����
def existProcessById(pid):
    return existProcessByIds([pid])

#�ж�ָ��id�Ľ����б��Ƿ����
def existProcessByIds(pidList, isAll = False):
    sql = 'select * from Win32_Process where ('
    for pid in pidList:
        if not sql.endswith('('):
            sql += ' or '
        sql += 'ProcessId = %d' % (pid,)
    sql += ')'
    count = autoutil.queryWmi(sql)[1]
    if isAll:
        return count == len(pidList)
    return count > 0

#�ж�ָ��name�Ľ����Ƿ����
def existProcessByName(pname):
    return existProcessByNames([pname])

#�ж�ָ��name�Ľ����б��Ƿ����
def existProcessByNames(pnameList, isAll = False):
    try:
        sql = 'select * from Win32_Process where ('
        for pname in pnameList:
            if not sql.endswith('('):
                sql += ' or '
            sql += 'Name = "%s"' % (pname,)
        sql += ')'
        rst, count = autoutil.queryWmi(sql)
        if isAll:
            pnameSet = set()
            for i in range(count):
                pnameSet.add(rst[i].Name.encode(sys.getfilesystemencoding()))
            return len(pnameSet) == len(pnameList)
        return count > 0
    except:
        print 'psutil query proc'
        pnames = getProcessNamesByPsutil()
        for pname in pnameList:
            if not pname.lower() in pnames:
                return False
        return True

#��ȡ�ӽ����б�
#rpidListΪ�Ѿ��ݹ���Ľ���id�б�
def getChildProcessIds(pid, rpidList = []):
    if pid in rpidList:
        return []
    rpidList = copy.copy(rpidList)
    rpidList.append(pid)
    rst, count = autoutil.queryWmi('select * from Win32_Process where ParentProcessId = %d' % pid)
    cpidSet = set()
    for i in range(count):
        if rst[i].ProcessId in rpidList:
            continue
        cpidSet.add(rst[i].ProcessId)
        cpidSet.update(getChildProcessIds(rst[i].ProcessId, rpidList))
    return list(cpidSet)

#��ȡ������id
def getParentProcessId(pid):
    rst, count = autoutil.queryWmi('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        return rst[0].ParentProcessId

#��ȡ���̵�GDI����
def getProcessGDI(pid):
    proc = autoutil.tryExcept(win32api.OpenProcess, win32con.PROCESS_ALL_ACCESS, 0, pid)
    if autoutil.isExcept(proc):
        return
    gdi = autoutil.tryExcept(win32process.GetGuiResources, proc.handle, win32con.GR_GDIOBJECTS)
    autoutil.tryExcept(proc.close)
    if not autoutil.isExcept(gdi):
        return gdi

#��ȡָ��name�Ľ���id
def getProcessIdByName(pname):
    rst, count = autoutil.queryWmi('select * from Win32_Process where Name = "%s"' % pname)
    if count:
        return rst[0].ProcessId

#��ȡָ��name�Ľ���id�б�
def getProcessIdsByName(pname):
    rst, count = autoutil.queryWmi('select * from Win32_Process where Name = "%s"' % pname)
    return [item.ProcessId for item in rst]

#��ȡָ��hwnd�Ľ���id,û�л�ȡ������1
def getProcessIdByHwnd(hwnd):
    rst = win32process.GetWindowThreadProcessId(hwnd)
    return rst[1]

#��ȡ����id�б�
def getProcessIds():
    rst, count = autoutil.queryWmi('select * from Win32_Process')
    pidList = []
    for i in range(count):
        pidList.append(rst[i].ProcessId)
    return pidList

#��ȡָ��id�Ľ���name
def getProcessNameById(pid):
    rst, count = autoutil.queryWmi('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        pname = autoutil.tryExcept(rst[0].Name.encode, sys.getfilesystemencoding())
        if not autoutil.isExcept(pname):
            return pname

#��ȡָ���û��Ľ���id�б�
def getUserProcessIds(user):
    rst, count = autoutil.queryWmi('select * from Win32_Process')
    pidList = []
    for i in range(count):
        owner = autoutil.tryExcept(rst[i].ExecMethod_, 'GetOwner')
        if not autoutil.isExcept(owner) and owner.User and owner.User.lower() == user.lower():
            pidList.append(rst[i].ProcessId)
    return pidList

#ɱ��ָ��id�Ľ���
def killProcessById(pid, user = None):
    killProcessByIds([pid], user)

#ɱ��ָ��id�Ľ����б�
def killProcessByIds(pidList, user = None):
    cmd = 'taskkill /F /T'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pid in pidList:
        cmd += ' /PID %d' % pid
    createProcess(cmd, True)

#ɱ��ָ��name�Ľ���
def killProcessByName(pname, user = None):
##    killProcessByNames([pname], user)
    cmd = r'taskkill /T /F /IM %s' % pname
    createProcess(cmd, True)

#ɱ��ָ��name�Ľ����б�
def killProcessByNames(pnameList, user = None):
    cmd = 'taskkill'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pname in pnameList:
        cmd += ' /IM "%s"' % pname
    createProcess(cmd, True)

#��ȡָ�����̵�����������
def getCmdLineById(pid):
    rst,count= autoutil.queryWmi('select * from Win32_Process where ProcessId=%s' % pid)
    if count:
        cmdLine = autoutil.tryExcept(rst[0].CommandLine.encode, sys.getfilesystemencoding())
        if not autoutil.isExcept(cmdLine):
            return cmdLine

#ö�ٽ��̼��ص�ģ���б�
def listProcessModules(pid):
    hprocess = None
    modules = []
    try:
        hprocess = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
        moduleinfo = win32process.EnumProcessModules(hprocess)
        for module in moduleinfo:
            modulefile = win32process.GetModuleFileNameEx(hprocess, module)
            modules.append(modulefile)
        return modules
    except:
        return modules
    finally:
        if hprocess:
            win32api.CloseHandle(hprocess)   

if __name__ == '__main__':
    print existProcessByNames(['360tray.exe'])
