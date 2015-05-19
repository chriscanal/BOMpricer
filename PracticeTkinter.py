#!/usr/bin/python

#This file was written by Chris Canal for iRobot
#If you have any questions or need help with
#a similair script, please contact me at
#chriscanal@chriscanal.com

#Got some help with parsing Json from:
#http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

#Import dependencies
import requests
import json
import pprint
import sys
import urllib2
import csv
import time
from random import randint
from pprint import pprint
from xml.dom import minidom
import yaml
import pprint
from Tkinter import *
import tkFileDialog
import glob


CSVMatrix = []

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
    CSVMatrix = csv.reader(out, skipinitialspace=False)
    CSVMatrix = [row for row in CSVMatrix]
    out.close()
    print CSVMatrix

if __name__ == "__main__":
    window = Window(None)
    window.title("Import CSV File")
    window.mainloop()
