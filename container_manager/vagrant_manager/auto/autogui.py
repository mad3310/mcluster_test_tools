#coding:gbk
"""
���ڲ����Զ�������
"""
import autoutil, autoinput
import ctypes
import re
import win32con, win32gui

#���ڻ���
class Window:
    @staticmethod
    def parseClickConfig(clkCfg):
        if clkCfg == None:
            return None, None, autoinput.CLICK_MOUSE
        if type(clkCfg) == int:
            return None, None, clkCfg
        if len(clkCfg) == 2:
            return clkCfg[0], clkCfg[1], autoinput.CLICK_MOUSE
        return clkCfg

    @staticmethod
    def parseTitleConfig(titleCfg):
        if type(titleCfg) == str:
            return titleCfg, None, False
        if len(titleCfg) == 2:
            if type(titleCfg[1]) == bool:
                return titleCfg[0], None, titleCfg[1]
            return titleCfg[0], titleCfg[1], False
        return titleCfg

    def __init__(self, hwnd):
        self.hwnd = hwnd

    #clkCfg:mode|(x,y)|(x,y,mode)
    def click(self, clkCfg = None):
        clickWindow(self.hwnd, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickFor(self, timeout, cond, clkCfg = None):
        return clickWindowFor(self.hwnd, timeout, cond, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForClose(self, timeout, hwnd, clkCfg = None):
        return clickWindowForClose(self.hwnd, timeout, hwnd, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForCloseSelf(self, timeout, clkCfg = None):
        return clickWindowForCloseSelf(self.hwnd, timeout, clkCfg)

    #timeout:timeout|(timeout,interval)
    #titleCfg:title|(title,parentTitle)|(title,isRaw)|(title,parentTitle,isRaw)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForFind(self, timeout, titleCfg, clkCfg = None):
        hwnd = clickWindowForFind(self.hwnd, timeout, titleCfg, clkCfg)
        if hwnd:
            return Window(hwnd)

    #timeout:timeout|(timeout,interval)
    #titleCfg:title|(title,isRaw)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForFindChild(self, timeout, titleCfg, clkCfg = None):
        hwnd = clickWindowForFindChild(self.hwnd, timeout, titleCfg, clkCfg)
        if hwnd:
            return Window(hwnd)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForHidden(self, timeout, hwnd, clkCfg = None):
        return clickWindowForHidden(self.hwnd, timeout, hwnd, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForHiddenSelf(self, timeout, clkCfg = None):
        return clickWindowForHiddenSelf(self.hwnd, timeout, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForMd5(self, timeout, hwnd, x, y, md5, clkCfg = None):
        return clickWindowForMd5(self.hwnd, timeout, hwnd, x, y, md5, clkCfg)

    #timeout:timeout|(timeout,interval)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForMd5Self(self, timeout, x, y, md5, clkCfg = None):
        return clickWindowForMd5Self(self.hwnd, timeout, x, y, md5, clkCfg)

    def getClass(self):
        return getWindowClass(self.hwnd)

    def getParent(self):
        hwnd = getParentWindow(self.hwnd)
        if hwnd:
            return Window(hwnd)

    def getRect(self):
        return getWindowRect(self.hwnd)

    def getText(self):
        return getWindowText(self.hwnd)

    def findChild(self, title, isRaw = False):
        hwnd = findWindow(title, self.hwnd, isRaw)
        if hwnd:
            return Window(hwnd)

    def findChilds(self, title, isRaw = False):
        hwndList = findWindows(title, self.hwnd, isRaw)
        return [Window(hwnd) for hwnd in hwndList]        

    def max(self):
        return maxWindow(self.hwnd)

    def min(self):
        return minWindow(self.hwnd)

    def setText(self, text):
        return setWindowText(self.hwnd, text)

    def show(self):
        showWindow(self.hwnd)

    def top(self):
        return topWindow(self.hwnd)

    def isVisible(self):
        return win32gui.IsWindowVisible(self.hwnd)

    def isEnabled(self):
        return win32gui.IsWindowEnabled(self.hwnd)

    def isDisabled(self):
        if not win32gui.IsWindowVisible(self.hwnd):
            return True
        if not win32gui.IsWindowEnabled(self.hwnd):
            return True

#�������
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindow(hwnd, clkCfg = None):
    if isRawWindow(hwnd):
        return
    topWindow(hwnd)
    rect = getWindowRect(hwnd)
    if not rect:
        return
    x, y, mode = Window.parseClickConfig(clkCfg)
    if x == None:
        x = (rect[0] + rect[2]) / 2
    elif x < 0:
        x += rect[2]
    else:
        x += rect[0]
    if y == None:
        y = (rect[1] + rect[3]) / 2
    elif y < 0:
        y += rect[3]
    else:
        y += rect[1]
    autoinput.clickMouse(x, y, False, mode)

#������ڵȴ���������
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowFor(hwnd, timeout, cond, clkCfg = None):
    def __clickWindowFor__(hwnd, cond, clkCfg):
        rst = cond.do()
        if not rst or autoutil.isExcept(rst):
            clickWindow(hwnd, clkCfg)
        return rst
    return autoutil.handleTimeout(__clickWindowFor__, timeout, hwnd, cond, clkCfg)

#������ڵȴ�ĳ���ڹر�
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForClose(hwnd, timeout, tgtHwnd, clkCfg = None):
    cond = autoutil.Condition(autoutil.negative, win32gui.IsWindow, tgtHwnd)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#������ڵȴ��ô��ڹر�
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForCloseSelf(hwnd, timeout, clkCfg = None):
    return clickWindowForClose(hwnd, timeout, hwnd, clkCfg)

#������ڵȴ��ҵ�ĳ����
#timeout:timeout|(timeout,interval)
#titleCfg:title|(title,isRaw)|(title,parentTitle)|(title,parentTitle,isRaw)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForFind(hwnd, timeout, titleCfg, clkCfg = None):
    title, parentTitle, isRaw = Window.parseTitleConfig(titleCfg)
    cond = autoutil.Condition(findWindow, title, parentTitle, isRaw)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#������ڵȴ��ҵ��ô��ڵ�ĳ�Ӵ���
#timeout:timeout|(timeout,interval)
#titleCfg:title|(title,isRaw)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForFindChild(hwnd, timeout, titleCfg, clkCfg = None):
    if type(titleCfg) == tuple:
        titleCfg = titleCfg[0], hwnd, titleCfg[1]
    else:
        titleCfg = titleCfg, hwnd
    return clickWindowForFind(hwnd, timeout, titleCfg, clkCfg)

#������ڵȴ�ĳ���ڲ��ɼ�
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForHidden(hwnd, timeout, tgtHwnd, clkCfg = None):
    cond = autoutil.Condition(autoutil.negative, win32gui.IsWindowVisible, tgtHwnd)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#������ڵȴ��ô��ڲ��ɼ�
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForHiddenSelf(hwnd, timeout, clkCfg = None):
    return clickWindowForHidden(hwnd, timeout, hwnd, clkCfg)

#������ڵȴ�ĳ�������������ƥ��md5
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForMd5(hwnd, timeout, tgtHwnd, x, y, md5, clkCfg = None):
    def __clickWindowForMd5__(hwnd, x, y, md5):
        if isRawWindow(hwnd):
            return False
        if not topWindow(hwnd):
            return False
        rect = getWindowRect(hwnd)
        if not rect:
            return False
        if x < 0:
            x += rect[2]
        else:
            x += rect[0]
        if y < 0:
            y += rect[3]
        else:
            y += rect[1]
##        grabStr = autoio.grab(x - 5, y - 5, x + 6, y + 6).tostring()
        return autoutil.md5(grabStr) == md5
    cond = autoutil.Condition(__clickWindowForMd5__, tgtHwnd, x, y, md5)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#������ڵȴ��ô������������ƥ��md5
#timeout:timeout|(timeout,interval)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForMd5Self(hwnd, timeout, x, y, md5, clkCfg = None):
    return clickWindowForMd5(hwnd, timeout, hwnd, x, y, md5, clkCfg)

#���ҵ�һ�����ڣ��������ɼ��������á�������
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findRawWindow(title, parentTitle = None):
    return findWindows(title, parentTitle, True, True)

#���Ҵ��ڣ��������ɼ��������á�������
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findRawWindows(title, parentTitle = None):
    return findWindows(title, parentTitle, True)

#���ҵ�һ������
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findWindow(title, parentTitle = None, isRaw = False):
    return findWindows(title, parentTitle, isRaw, True)

#���Ҵ���
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findWindows(title, parentTitle = None, isRaw = False, returnFirst = False):
    def __fillWindowAttrs__(hwnd, rst):
        if not returnFirst:
            rst.add(hwnd)
        elif __matchWindow__(hwnd, title):
            rst.add(hwnd)
            return
    def __enumChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        rst = set()
        if not hwnd:
            autoutil.tryExcept(win32gui.EnumWindows, __fillWindowAttrs__, rst)
        else:
            autoutil.tryExcept(win32gui.EnumChildWindows, hwnd, __fillWindowAttrs__, rst)
            crst = set()
            for hcwnd in rst:
                if hcwnd not in hwnds:
                    crst.update(__enumChildWindows__(hcwnd, hwnds))
            rst.update(crst)
        return rst
    def __findChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        rst = set()
        hcwnd = autoutil.tryExcept(win32gui.FindWindowEx, hwnd, None, None, None)
        while hcwnd and not autoutil.isExcept(hcwnd) and hcwnd not in hwnds:
            __fillWindowAttrs__(hcwnd, rst)
            if hwnd:
                rst.update(__findChildWindows__(hcwnd, hwnds))
            hcwnd = autoutil.tryExcept(win32gui.FindWindowEx, hwnd, hcwnd, None, None)
        return rst
    def __getChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        rst = set()
        hcwnd = autoutil.tryExcept(win32gui.GetWindow, hwnd or win32gui.GetDesktopWindow(), win32con.GW_CHILD)
        while hcwnd and not autoutil.isExcept(hcwnd) and hcwnd not in hwnds:
            __fillWindowAttrs__(hcwnd, rst)
            if hwnd:
                rst.update(__getChildWindows__(hcwnd, hwnds))
            hcwnd = autoutil.tryExcept(win32gui.GetWindow, hcwnd, win32con.GW_HWNDNEXT)
        return rst
    def __matchWindow__(hwnd, title):
        if not isRaw and isRawWindow(hwnd):
            return False
        if type(title) == int:
            return win32gui.GetDlgCtrlID(hwnd) == title
        text = re.split('(\r|\n)+', getWindowText(hwnd))[0].strip()
        if text == title or re.match('^' + title + '$', text, re.S):
            return True
        clazz = getWindowClass(hwnd).strip()
        if clazz == title or re.match('^' + title + '$', clazz, re.S):
            return True
        return False
    if not parentTitle:
        hpwndList = [None]
    elif type(parentTitle) == int:
        hpwndList = [parentTitle]
    else:
        hpwndList = findRawWindows(parentTitle)
    rst = set()
    for hpwnd in hpwndList:
        rst.update(__enumChildWindows__(hpwnd, set()))
        if returnFirst and rst:
            return rst.pop()
        rst.update(__findChildWindows__(hpwnd, set()))
        if returnFirst and rst:
            return rst.pop()
        rst.update(__getChildWindows__(hpwnd, set()))
        if returnFirst and rst:
            return rst.pop()
    if returnFirst:
        return 0
    else:
        lst = []
        for hwnd in rst:
            if __matchWindow__(hwnd, title):
                lst.append(hwnd)
        return lst

#��ȡ����ߴ�
def getDesktopRect():
    return getWindowRect(win32gui.GetDesktopWindow())

#��ȡ������
def getParentWindow(hwnd):
    hwnd = autoutil.tryExcept(win32gui.GetParent, hwnd)
    if not autoutil.isExcept(hwnd):
        return hwnd

#��ȡ��������
def getWindowClass(hwnd, buf = ctypes.create_string_buffer(1024)):
    size = ctypes.sizeof(buf)
    ctypes.memset(buf, 0, size)
    ctypes.windll.user32.GetClassNameA(hwnd, ctypes.addressof(buf), size)
    return buf.value.strip()

#��ô��ڳߴ�
def getWindowRect(hwnd):
    rect = autoutil.tryExcept(win32gui.GetWindowRect, hwnd)
    if not autoutil.isExcept(rect):
        return rect

#��ȡ��������
def getWindowText(hwnd, buf = ctypes.create_string_buffer(1024)):
    size = ctypes.sizeof(buf)
    ctypes.memset(buf, 0, size)
    autoutil.tryExcept(win32gui.SendMessageTimeout, hwnd, win32con.WM_GETTEXT, size, buf, win32con.SMTO_ABORTIFHUNG, 30)
    return buf.value.strip()

#���ô�������
def setWindowText(hwnd, text):
    rst = autoutil.tryExcept(win32gui.SendMessageTimeout, hwnd, win32con.WM_SETTEXT, 0, text, win32con.SMTO_ABORTIFHUNG, 30)
    return not autoutil.isExcept(rst)

#�ж��Ƿ�Ϊ����������
def isRawWindow(hwnd):
    return not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd) or ctypes.windll.user32.IsHungAppWindow(hwnd)

#��󻯴���
def maxWindow(hwnd):
    return win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED) and topWindow(hwnd)

#��С������
def minWindow(hwnd):
    return win32gui.ShowWindow(hwnd, win32con.SW_SHOWMINIMIZED)

#��ʾĬ�ϴ���
def showWindow(hwnd):
    return win32gui.ShowWindow(hwnd, win32con.SW_SHOWDEFAULT) and topWindow(hwnd)

#�ö�����
def topWindow(hwnd):
    hwndList = [hwnd]
    while True:
        hwnd = getParentWindow(hwnd)
        if not hwnd:
            break
        hwndList.append(hwnd)
    topHwnd = None
    while len(hwndList) > 0:
        hwnd = hwndList.pop()
        if not isRawWindow(hwnd):
            topHwnd = hwnd
            break
    if not topHwnd:
        return False
    place = autoutil.tryExcept(win32gui.GetWindowPlacement, topHwnd)
    if autoutil.isExcept(place):
        return False
    if place[1] == win32con.SW_SHOWMINIMIZED and not showWindow(topHwnd):
        return False
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == topHwnd:
        return True
    rst = autoutil.tryExcept(win32gui.SetForegroundWindow, topHwnd)
    if not autoutil.isExcept(rst):
        return True
    return getWindowClass(hwnd) == 'Progman' and getWindowText(hwnd) == 'Program Manager'


#��ʾ��Ϣ��
def alertMessage(msg, text = '', style = win32con.MB_ICONINFORMATION):
    return win32gui.MessageBox(None, msg, text, style|win32con.MB_SYSTEMMODAL)

#��ʾ�����
def alertError(error, text = ''):
    return alertMessage(error, text, win32con.MB_ICONERROR)

#��ʾѡ���
def alertChoice(choice, text = ''):
    return alertMessage(choice, text, win32con.MB_YESNO|win32con.MB_ICONQUESTION) == win32con.IDYES
