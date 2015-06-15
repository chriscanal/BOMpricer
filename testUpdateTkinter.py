#!/usr/bin/env python
import datetime
from Tkinter import *

class MyApp(object):
    def __init__(self):
        self.root = Tk()
        self.time_var = StringVar()
        self.time_var.set('...')
        self._init_widgets()

    def _init_widgets(self):
        self.label = Label(self.root, textvariable=self.time_var)
        frame = Frame(self.root)
        self.frame = frame
        self.button = Button(frame, text = "update time", command = self._on_button_click)
        self.frame.grid()
        self.button.grid()
        self.label.grid()

    def _on_button_click(self):
        self.time_var.set(str(datetime.datetime.now()))
        # uncomment these lines to get a broken code
        #self.frame.grid_remove()
        #self.frame = Frame(self.root)
        #self.frame.grid()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MyApp()
    app.run()
