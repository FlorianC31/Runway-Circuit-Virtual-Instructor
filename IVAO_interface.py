import keyboard
import time
import win32com.client
import win32gui
import win32con
import pywinauto
import sys


class Window:
    def __init__(self, window_name, scale=1):
        self.name = window_name
        self.scale = scale
        self.x_init = 0
        self.hwnd = self.get_hwnd()

    def is_open(self):
        return self.get_hwnd() > 0

    def show(self):
        if self.is_open():
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            while not self.is_focus():
                time.sleep(0.1)
                win32gui.ShowWindow(self.get_hwnd(), win32con.SW_NORMAL)
                win32gui.SetForegroundWindow(self.get_hwnd())
        else:
            print('ERROR: Enable to show ', self.name, ' because it is not opened')
            sys.exit(0)

    def get_hwnd(self):
        thelist = []

        def findit(hwnd, wnd_name):
            # print(win32gui.GetWindowText(hwnd))
            if win32gui.GetWindowText(hwnd).startswith(wnd_name):  # check the title
                thelist.append(hwnd)
                # return hwnd

        win32gui.EnumWindows(findit, self.name)
        return thelist[0]

    def close(self):
        print("Fermeture de", self.name)
        # win32gui.CloseWindow(self.get_hwnd())
        win32gui.PostMessage(self.get_hwnd(), win32con.WM_CLOSE, 0, 0)

    def x_move(self, x, absolute=True):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if absolute:
                win32gui.MoveWindow(self.get_hwnd(), x, rect[1], width, height, True)
            else:
                win32gui.MoveWindow(self.get_hwnd(), rect[0] + x, rect[1], width, height, True)

    def y_move(self, y, absolute=True):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if absolute:
                win32gui.MoveWindow(self.get_hwnd(), rect[0], y, width, height, True)
            else:
                win32gui.MoveWindow(self.get_hwnd(), rect[0], rect[1] + y, width, height, True)

    def resize(self, w, h):
        if self.is_open():
            rect = win32gui.GetWindowRect(self.get_hwnd())
            win32gui.MoveWindow(self.get_hwnd(), rect[0], rect[1], w, h, True)

    def click(self, x_relative, y_relative, double_click=False):
        if self.is_open():
            self.show()
            rect = win32gui.GetWindowRect(self.get_hwnd())
            x = rect[0] + int(x_relative * self.scale)
            y = rect[1] + int(y_relative * self.scale)

            if double_click:
                pywinauto.mouse.double_click(button='left', coords=(x, y))
            else:
                pywinauto.mouse.click(button='left', coords=(x, y))

        else:
            print('ERROR:', self.name, 'is not opened')
            sys.exit(0)

    def is_focus(self):
        return win32gui.GetForegroundWindow() == self.get_hwnd()

    def set_x_init(self, x=0):
        if x == 0:
            rect = win32gui.GetWindowRect(self.get_hwnd())
            self.x_init = rect[0]
        else:
            self.x_init = x

    def send_txt(self, pos_x, pos_y, text):
        self.show()
        self.click(pos_x, pos_y)
        keyboard.write(text)
        keyboard.press_and_release('enter')


if __name__ == '__main__':
    ivao_window = Window("IVAO Pilot Client")
    msfs_window = Window("Microsoft Flight Simulator")

    print(ivao_window.hwnd)
    print(msfs_window.hwnd)
