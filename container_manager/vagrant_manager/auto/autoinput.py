#coding:gbk
"""
�������Զ�������
"""
import time
import win32api, win32con

CLICK_MOUSE = 0
CLICK_MOUSE_DOUBLE = 1
CLICK_MOUSE_RIGHT = 2
MOVE_MOUSE = 3

#������
def clickMouse(x, y, byDrv = False, mode = CLICK_MOUSE):
    moveMouse(x, y, byDrv)
    if mode == MOVE_MOUSE:
        return
    downMsg, upMsg = win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP
    if mode == CLICK_MOUSE_RIGHT:
        downMsg, upMsg = win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP
    win32api.mouse_event(downMsg, 0, 0, 0, 0)
    win32api.mouse_event(upMsg, 0, 0, 0, 0)
    if mode == CLICK_MOUSE_DOUBLE:
        win32api.mouse_event(downMsg, 0, 0, 0, 0)
        win32api.mouse_event(upMsg, 0, 0, 0, 0)

#�����꣨���˫����
def clickMouseDouble(x, y, byDrv = False):
    clickMouse(x, y, byDrv, CLICK_MOUSE_DOUBLE)

#�����꣨�Ҽ���
def clickMouseRight(x, y, byDrv = False):
    clickMouse(x, y, byDrv, CLICK_MOUSE_RIGHT)

#�ƶ����
def moveMouse(x, y, byDrv = False):
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    x, y = int(float(x) / w * 65535), int(float(y) / h * 65535)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)

#��ȡ��ǰ����
def getCursorPos():
    return win32api.GetCursorPos()
