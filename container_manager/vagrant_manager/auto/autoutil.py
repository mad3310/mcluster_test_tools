#coding:gbk

import hashlib
#import ImageGrab
import logging
#import MySQLdb
import pywintypes
import random
import sys
import os
import threading, time
import win32con, win32file, wmi
import pythoncom
import ctypes

overlapped = None

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12

FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED  = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED  = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

def _print(_str, color=FOREGROUND_WHITE):
    set_color(color)
    sys.stdout.write(_str+'\n')
    sys.stdout.flush()
    set_color(FOREGROUND_WHITE)
    
#读写锁
class RWLock():
    def __init__(self):
        self.readers = 0
        self.wLock = threading.Lock()
        self.rLock = threading.Lock()
        
    def writeAcquire(self):
        self.wLock.acquire()
        
    def writeRelease(self):
        self.wLock.release()
        
    def readAcquire(self):
        self.rLock.acquire()
        self.readers += 1
        if self.readers == 1:
            self.wLock.acquire()
        self.rLock.release()
        
    def readRelease(self):
        self.rLock.acquire()
        self.readers -= 1
        if self.readers == 0:
            self.wLock.release()
        self.rLock.release()



#条件对象
class Condition:
    def __init__(self, func, *params, **paramMap):
        self.func = func
        self.params = params
        self.paramMap = paramMap

    def do(self):
        return self.func(*self.params, **self.paramMap)

#函数线程
class FuncThread(threading.Thread):
    def __init__(self, func, *params, **paramMap):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        self.paramMap = paramMap
        self.rst = None
        self.finished = False

    def run(self):
        pythoncom.CoInitialize()
        self.rst = self.func(*self.params, **self.paramMap)
        self.finished = True
        pythoncom.CoUninitialize()

    def getResult(self):
        return self.rst

    def isFinished(self):
        return self.finished

#数据对象
class Data:
    def __init__(self, data = None):
        self.data = data

    def get(self):
        return self.data

    def set(self, data):
        self.data = data


#日志对象
class Logger:
    def __init__(self, path):
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        self.logger.addHandler(sh)
        fh = logging.FileHandler(path)
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

    def debug(self, *data):
        data = ' '.join(map(str, data))
        self.info(data, logging.DEBUG, FOREGROUND_WHITE|FOREGROUND_INTENSITY)

    def error(self, data, color=FOREGROUND_RED):
        self.info(data, logging.ERROR, color|FOREGROUND_INTENSITY)

    def fatal(self, data, color = FOREGROUND_GREEN):
        self.info(data, logging.FATAL)

    def info(self, data, level = logging.INFO, color = FOREGROUND_GREEN):
        set_color(color|FOREGROUND_INTENSITY)
        self.logger.log(level, data)
        set_color(FOREGROUND_WHITE)

    def warn(self, data, color=FOREGROUND_YELLOW):
        self.info(data, logging.WARN, color|FOREGROUND_INTENSITY)

#获取某区域指定像素的数量
#rgb:(r,g,b)
def countPixels(rect, rgb):
    img = grabImage(rect)
    w, h = rect[2] - rect[0], rect[3] - rect[1]
    num = 0
    for i in range(w):
        for j in range(h):
            if img.getpixel((i, j)) == rgb:
                num += 1
    return num

#在线程中执行
def doInThread(func, *params, **paramMap):
    ft = FuncThread(func, *params, **paramMap)
    ft.start()
    return ft

##获取指定区域的截图
#def grab(rect, path = None):
    #img = ImageGrab.grab(rect)
    #if path:
        #img.save(path)
    #return img

#获取屏幕截图
def grabScreen(path = None):
    return grab(None, path)

##获取某区域的截图
#def grabImage(rect, filename = None):
    #img = ImageGrab.grab(rect)
    #if filename:
        #img.save(filename)
    #return img

#获取指定位置的像素
def getPixel(x, y):
    img = grab((x, y, x + 1, y + 1))
    return img.getpixel((0, 0))

#获取区域内指定像素的数量
#rgb:(r,g,b)
def countPixel(rect, rgb):
    img = grab(rect)
    num = 0
    for i in range(rect[2] - rect[0]):
        for j in range(rect[3] - rect[1]):
            if img.getpixel((i, j)) == rgb:
                num += 1
    return num

#判断指定位置是否与像素匹配
#rgb:(r,g,b)
def matchPixel(x, y, rgb):
    return getPixel(x, y) == rgb

#在一定次数内执行
def doInTimes(func, times, *params, **paramMap):
    while times > 0:
        rst = func(*params, **paramMap)
        if rst and not isExcept(rst):
            break
        times = times - 1
    return rst

#在超时范围内执行
#timeout为数值或元组（超时时长,间隔时间）
def handleTimeout(func, timeout, *params, **paramMap):
    interval = 0.6
    if type(timeout) == tuple:
        timeout, interval = timeout
    rst = None
    while timeout > 0:
        t = time.time()
        rst = func(*params, **paramMap)
        if rst and not isExcept(rst):
            break
        time.sleep(interval)
        timeout -= time.time() - t
    return rst

#判断是否为异常
def isExcept(e, eType = Exception):
    return isinstance(e, eType)

#判断是否为64位系统
def isSystem64():
    return 'PROGRAMFILES(X86)' in os.environ

#计算md5
def md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

#计算文件md5
def md5File(path, size = 32768):
    m = hashlib.md5()
    f = open(path, 'rb')
    while True:
        d = f.read(size)
        if not d:
            break
        m.update(d)
    f.close()
    return m.hexdigest()

#计算sha1
def sha1(data):
    m = hashlib.sha1()
    m.update(data)
    return m.hexdigest()

#计算文件sha1
def sha1File(path, size = 32768):
    m = hashlib.sha1()
    f = open(path, 'rb')
    while True:
        d = f.read(size)
        if not d:
            break
        m.update(d)
    f.close()
    return m.hexdigest()

#计算截图的md5
def md5Image(rect):
    img = grabImage(rect)
    return md5(img.tostring())

#计算截图md5
def md5Grab(rect):
    img = grab(rect)
    return md5(img.tostring())

#取反执行
def negative(func, *params, **paramMap):
    return not func(*params, **paramMap)

#查询WMI服务
def queryWmi(sql):
    rst = wmi.WMI().ExecQuery(sql)
    count = tryExcept(len, rst)
    if isExcept(count):
        return queryWmi(sql)
    return rst, count

#获取随机数字串
def randomIntStr():
    return str(random.random())[2:]

#获取时间戳
def timestamp(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

#获取文件创建时间
def getFileCreateTime(file_path, style='%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime(os.stat(file_path).st_ctime))

#获取文件更改时间
def getFileModifyTime(file_path, style='%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime(os.stat(file_path).st_mtime))

#获取文件最后访问时间
def getFileModifyTime(file_path, style='%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime(os.stat(file_path).st_atime))

#在try中执行
def tryExcept(func, *params, **paramMap):
    try:
        return func(*params, **paramMap)
    except Exception, e:
        return e

#锁文件
def lockFile(file):
    global overlapped
    if not overlapped:
        overlapped = pywintypes.OVERLAPPED()
    hfile = win32file._get_osfhandle(file.fileno())
    win32file.LockFileEx(hfile, win32con.LOCKFILE_EXCLUSIVE_LOCK, 0, 0xffff, overlapped)

#解锁文件
def unlockFile(file):
    hfile = win32file._get_osfhandle(file.fileno())
    win32file.UnlockFileEx(hfile, 0, 0xffff, overlapped)