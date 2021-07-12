import tkinter

#All library dependencies across all classes (are used in class file):
#import serial
#import numpy as np
#import subprocess
#import time
#import os
#import sys
#import tkinter.messagebox as msgbox
#import tkinter.filedialog as fileDialog
#from tkinter.simpledialog import askstring
#import ctypes as ct
#import pyvisa as pv
#from shutil import copyfile

from Connections_Classes_Ver2 import allNonCamConnectClass, camera
from Experiment_RunningLoadingDesign_Classes_Ver2 import experimentClass

#Code by: Alexander Mayton

debug = True

def TurnOff(serialObj): 
    ''' serialObj - pass the allNonCamConnect object that contains the shutter,
    pgen, and vgen controls.
    
    Function to safely close the GUI, DO NOT close the gui by clicking the X
    because if you try to reopen the ports when spyder remembers the serial 
    objects it will throw an error
    
    RETURN: NONE (ends the program)'''
    if serialObj.shutterReady:
        try:
            serialObj.Shutter.close()
            print('Shutter serial closed')
        except:
            print("Shutter serial connection hasn't been opened, so it can't be closed")
    if serialObj.pgenReady:
        try:
            serialObj.Pgen.close()
            print('PGen serial closed')
        except:
            print("Pgen serial connection hasn't been opened, so it can't be closed")
    if serialObj.serialReady:
        try:
            serialObj.VGen.close()
            print('Vgen visa connection closed')
        except:
            print("Vgen serial connection hasn't been opened, so it can't be closed")
    serialObj.master.destroy()
    return

mainMenu = tkinter.Tk()
mainMenu.title('Experimental Control')

#camera object - contains the camera connection and camera parts of the GUI
cam = camera(mainMenu)
cam.camFrame.grid(row=0,column=0,padx=5)

#All serial and Visa stuff - connections and their part of the GUI
ncc = nonCamConnections = allNonCamConnectClass(mainMenu)
ncc.cif.grid(row=0,column=1)

#Exit Button
offButton = tkinter.Button(mainMenu,
                           command= lambda: TurnOff(ncc),
                           text='Exit')
offButton.grid(row=0,column=2,padx=10)

#These are the formats of each of the channels, each star represents another
#non-time parameter
camFormat = ',*,*,*'
PFormat = ',*'
VFormat = ',*'
shutterFormat = ',*'

#(all times in exp design file are in seconds)
#Experiment running and design GUI parts and functions
es = allExperimentStuff = experimentClass(mainMenu,
                                          cam,
                                          ncc,
                                          camFormat,
                                          PFormat,
                                          VFormat,
                                          shutterFormat)
es.ebf.grid(row=1,column=0,pady=5,padx=5)

#if we're in debug mode, we have a part of the GUI to print values of the
#objects
if debug:
    def infoDump(nonCamObj):
        '''
        nonCamObj: allNonCamConnectClass object we want the values of
        
        return: NONE
        
        Prints values of nonCamObj to the console so that we can debug. Access
        this function by pressing the printAllInfoButton on the GUI.

        '''
        print(nonCamObj.pgenCoord)
        return
    
    printAllInfoButton = tkinter.Button(mainMenu,
                        command=lambda:infoDump(ncc),
                        text="Print all available main variable info to console")
    printAllInfoButton.grid(row=2,column=0,pady=5)

mainMenu.mainloop()