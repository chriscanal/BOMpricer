#!/usr/bin/python

from Tkinter import *
import tkFileDialog
import csv, os.path, glob, sys


class Window(Tk):

  def __init__(self, parent):
    Tk.__init__(self, parent)
    self.parent = parent
    self.initialize()
    
    self.dir_opt = options = {}
    options['initialdir'] = 'C:\\'
    options['mustexist'] = False
    options['parent'] = self.parent

  def initialize(self):
    self.geometry("600x400+30+30")
    self.wButton = Button(self, text='Import', command = self.OnButtonClick)
    self.wButton.pack()
    self.check = Checkbutton(text="Digikey Only")
    self.check.pack()

  def OnButtonClick(self):
    self.top = Toplevel()
    self.top.title("Browse For File")
    self.top.geometry("300x150+30+30")
    self.top.transient(self)
    self.wButton.config(state='disabled')
    button_opt = {'padx': 5, 'pady': 5}
    self.topButton = Button(self.top, text='Open Directory', command=self.file_save)
    self.topButton.pack()
    
  def file_save(self):
    f = tkFileDialog.askopenfilename()
    out = open(f, 'r')
    CSVdata = csv.reader(out, skipinitialspace=False)
    CSVdata = [row for row in CSVdata]
    out.close()
    print CSVdata

  
if __name__ == "__main__":
    window = Window(None)
    window.title("Import CSV File")
    window.mainloop()
    
    
    
