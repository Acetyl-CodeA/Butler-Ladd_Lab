# -*- coding: utf-8 -*-
"""
All experiment stuff

Def needs updating

I think the new advanced options will not be in the changed parameters
of an experiment so it won't effect loading, design, or format
"""

"""
Importable class for Design Experiment also data search import function
"""

import tkinter
import tkinter.messagebox as msgbox
import sys
import tkinter.filedialog as fileDialog
from tkinter.simpledialog import askstring
import numpy as np
import os
import time
from shutil import copyfile

class experimentClass(object):
    ''' Object containing all methods for running, loading, and designing
        experiments.
        
        Initialization parameters:
        
        master_: Highest level tkinter object that this instance of
        experimentClass will be placed into.
        master_: tkinter.tk() object.
        
        camObject: Contains the camera library and camera connection we want to
        use in the experiment.
        type camObject: camera object.
        
        nonCamObject: Contains all non-camera connections that we want to use
        in the experiment.
        type nonCamObject: allNonCamConnectClass object.
        
        cameraFormatIN: Describes how the vector should be formatted for the
        camera channel.
        type cameraFormatIN: String.
        VGenFormatIN: Describes how the vector should be formatted for the
        VGen channel.
        type VGenFormatIN: String.
        PGenFormatIN: Describes how the vector should be formatted for the
        Pgen channel.
        PGenFormatIN: String.
        shutterFormatIN: Describes how the vector should be formatted for the
        shutter channel.
        shutterFormatIN: String.
        
        Needs updating
    '''
    
    def __init__(self,
                 master_,
                 camObject,
                 nonCamObject,
                 cameraFormatIN,
                 VGenFormatIN,
                 PGenFormatIN,
                 shutterFormatIN):
        '''
        Needs updating
        :param master_: DESCRIPTION
        :type master_: TYPE
        :param camObject: DESCRIPTION
        :type camObject: TYPE
        :param nonCamObject: DESCRIPTION
        :type nonCamObject: TYPE
        :param cameraFormatIN: DESCRIPTION
        :type cameraFormatIN: TYPE
        :param VGenFormatIN: DESCRIPTION
        :type VGenFormatIN: TYPE
        :param PGenFormatIN: DESCRIPTION
        :type PGenFormatIN: TYPE
        :param shutterFormatIN: DESCRIPTION
        :type shutterFormatIN: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        '''

        self.experimentPlanReady = False
        self.consolePrintStdOut = sys.stdout
        
        self.master = master_
        self.__cam = camObject
        self.__ncc = nonCamObject
        
        self.__cameraFormat = cameraFormatIN
        self.__VGenFormat = VGenFormatIN
        self.__PGenFormat = PGenFormatIN
        self.__shutterFormat = shutterFormatIN
        
        #EBF = experiment button frame
        self.ebf = tkinter.Frame(self.master,relief='solid',borderwidth=1)        
        self.ebfTitle = tkinter.Label(self.ebf,text= 'Experiment')
        self.ebfTitle.grid(row=0,column=0,pady=5)
        
        self.readyIndicator = tkinter.Label(self.ebf,text='Not Ready',bg='red')
        self.readyIndicator.grid(row=0,column=1,padx=3)
        self.readyCheckButton = tkinter.Button(self.ebf,
                                               text="Ready Check",
                                               bg='red',
                                               command=self.readyUpdater)
        self.readyCheckButton.grid(row=1,column=1)
        
        self.loadExpButton = tkinter.Button(self.ebf,text='Load Experiment',
                                            bg='red',
                                            command=self.loadExperiment)
        self.loadExpButton.grid(row=1,column=0,padx=3,pady=3)
        
        self.runExpButton = tkinter.Button(self.ebf,
                                           text='Run Experiment',
                                           command=self.experimentStartDialog)
        self.runExpButton.grid(row=2,column=0,padx=3,pady=3)
        
        self.designExpButton = tkinter.Button(self.ebf,
                                              text='Design Experiment',
                                              command=self.designWindowSetup)
        self.designExpButton.grid(row=2,column=1,padx=3,pady=3)
        
        self.debugLabel = tkinter.Label(self.ebf,
            text="Run experiment in debug mode (print events to console instead of file)")
        self.debugLabel.grid(row=3,column=0,columnspan=2)
        
        self.expDebState = tkinter.IntVar()
        self.debugCheckbox = tkinter.Checkbutton(self.ebf,
                                                 variable=self.expDebState,
                                                 relief='raised',
                                                 bg='purple')
        self.debugCheckbox.grid(row=4,column=0,columnspan=2)
        
        return

    def fileDataSearch(self,startingPhrase,searchedString,endingCharacter=';'):
        
        '''
        startingPhrase is a string that indicates what is the start of a data entry
        
        I've intentionally coded it open so we can add more entries if necessary so 
        we can increase the number of things the code manipulates later
        
        searchedString is the string we are looking inside of for startingPhrase
        
        endingCharacter is what tells us that that data set terminates it defaults 
        to semicolon but if someone wants to change it, be my guest, just pass it 
        an argument to replace it
        
        V5 up to date
        '''
        
        LSP = len(startingPhrase) #just shorthand for Length of Starting Phrase
        for check in range(len(searchedString)-LSP): 
            #looking through searchedString for startingPhrase
            if searchedString[check:LSP+check] == startingPhrase: #we find a match
                endChar = '0'
                for i in range(check,len(searchedString)):
                    endChar = searchedString[i]
                    if endChar == endingCharacter: #looking for the end of the phrase
                        foundPhrase = searchedString[check:i]
                        phraseEndNumber = i
                        for j in range(len(foundPhrase)):
                            #seperating each set of data in (each set of parentheses) into a list
                            if foundPhrase[j] =='(': #found a new data set
                                data = foundPhrase[j:phraseEndNumber]
                                ldtc = len(data)
                                ptl = []
                                for i in range(ldtc):
                                    if data[i] == '(':
                                        j = i
                                        while data[j] != ')': 
                                            #search till the end of the data set
                                            j += 1
                                            if j > ldtc:
                                                return -1,'error, no closing parentheses',-1
                                        try:
                                            bit = data[i+1:j] 
                                            #this is the data inside the set
                                            temp = bit.split(',') 
                                            #we take out the commas and make the set a list
                                            for k in range(len(temp)):
                                                temp[k] = float(temp[k]) 
                                                #we convert everything to numbers
                                        except:
                                            return -1,'error, non digit character found in data',-1
                                        ptl.append(tuple(temp))
                                        '''we add append the list of
                                        that one data set as a tuple to the ultimate list
                                        containing all the data sets in this phrase'''
                                        
                                return tuple(ptl) 
                                '''we return the list containing all the data sets 
                                of this phrase, as a tuple'''
                                
                        return -1,'no parentheses starts',-1           
                return -1,'could not find end',-1
        return -1,'could not find beginning',-1  
    
    def designWindowSetup(self):
        """
        Creates an instance of the designWindow class, which will pop
        up the design window.
        
        return: NONE
        
        V5 up to date
        """
        self.dw = designWindow(True,
                               self.__cameraFormat,
                               self.__VGenFormat,
                               self.__PGenFormat,
                               self.__shutterFormat)
        return
    
    def loadExperiment(self): 
        """
        Creates a file dialog to load an experiment design file. Will then
        check to make sure that the file is formatted and ordered correctly.
        It will tell you what's wrong with it if it can, or it will show the
        data once it is successfully loaded.
        
        return: NONE (Sets cameraData, VGendata, PGendata, and ShutterData)
        
        V5 up to date
        """
        #the first number in any/all data parentheses groups MUST be time
        try:
            self.filename =  fileDialog.askopenfilename(initialdir = os.getcwd(),
                            title = "Select file",
                            filetypes = (("text files","*.txt"),
                                         ("all files","*.*")))
            self.SavedExperimentFile = open(self.filename)
            
            #seftas = saved experiment file text as string
            self.seftas = self.SavedExperimentFile.read()
            self.SavedExperimentFile.close()
            
            self.cameraData = self.fileDataSearch('Camera:',self.seftas)
            
            if self.cameraData[0] == -1:
                msgbox.showerror(title='There was a problem with the text file',
                                 message=self.cameraData[1])
                self.cameraSuccess = False
            
            #VOOTSD is verify order of time sensitive data, make sure it's
            #in chronological order.
            elif not self.VOOTSD(self.cameraData):
                msgbox.showerror(title='Unordered data [Camera]',
                                 message="The first value in each () set is" \
                                 + " time, () must be in order by time")
                self.cameraSuccess = False
            else:
                self.cameraData = np.array(self.cameraData)
                msgbox.showinfo(title='Success',
                                message='Camera data in file at:\n' \
                                +self.filename \
                                +'\nsuccessfully loaded')
                msgbox.showinfo(message='Camera data:\n'+str(self.cameraData))
                self.cameraSuccess = True
            
            self.VGenData = self.fileDataSearch('VGen:',self.seftas)
            
            if self.VGenData[0] == -1:
                msgbox.showerror(title='There was a problem with the text file',
                                 message=self.VGenData[1])
                self.VGenSuccess = False
            elif not self.VOOTSD(self.VGenData):
                msgbox.showerror(title='Unordered data [VGen]',
                                 message="The first value in each () set is" \
                                 +" time, () must be in order by time")
                self.VGenSuccess = False
            else:
                self.VGenData = np.array(self.VGenData)
                msgbox.showinfo(title='Success',
                                message='VGen data in file at:\n' \
                                +self.filename \
                                +'\nsuccessfully loaded')
                msgbox.showinfo(message='VGen data:\n'+str(self.VGenData))
                self.VGenSuccess = True
           
            self.PGenData = self.fileDataSearch('PGen:',self.seftas)
            
            if self.PGenData[0] == -1:
                msgbox.showerror(title='There was a problem with the text file',
                                 message=self.PGenData[1])
                self.PGenSuccess = False
            elif not self.VOOTSD(self.PGenData):
                msgbox.showerror(title='Unordered data [PGen]',
                                 message="The first value in each () set is" \
                                 +" time, () must be in order by time")
                self.PGenSuccess = False
            else:
                self.PGenData = np.array(self.PGenData)
                msgbox.showinfo(title='Success',
                                message='PGen data in file at:\n' \
                                    +self.filename\
                                    +'\nsuccessfully loaded')
                msgbox.showinfo(message='PGen data:\n'+str(self.PGenData))
                self.PGenSuccess = True
            
            self.ShutterData = self.fileDataSearch('Shutter:',self.seftas)
            
            if self.ShutterData[0] == -1:
                msgbox.showerror(title='There was a problem with the text file'
                                 ,message=self.ShutterData[1])
                self.ShutterSuccess = False
            elif not self.VOOTSD(self.ShutterData):
                msgbox.showerror(title='Unordered data [Shutter]',
                                 message='The first value in each () set is' \
                                 + " time, () must be in order by time")
                self.ShutterSuccess = False
            else:
                self.ShutterData = np.array(self.ShutterData)
                msgbox.showinfo(title='Success',
                                message='Shutter data in file at:\n' \
                                    +self.filename \
                                    +'\nsuccessfully loaded')
                msgbox.showinfo(message='Shutter data:\n'+str(self.ShutterData))
                self.ShutterSuccess = True

        except:
            msgbox.showerror(title='An exception has occured',
                             message=str(sys.exc_info()[0]))
            
            '''I can't catch any 'FileNotFoundError' exceptions that occur due 
            to the user clicking 'cancel' just know that if you see one,
            nothing is wrong.'''
            
            print(sys.exc_info()[0])
            return
        
        for a in self.cameraData:
            if a[1] != int(a[1]):
                self.cameraSuccess = False
                msgbox.showerror(title="Int error",
                                 message="Number of frames must be an integer")
                break
        
        for b in self.ShutterData:
            if b[1] != int(b[1]):
                self.ShutterSuccess = False
                msgbox.showerror(title="Int error",
                                 message="Shutter state must be an integer")
                break
        
        if self.cameraSuccess \
            and self.VGenSuccess \
            and self.PGenSuccess \
            and self.ShutterSuccess:
            self.loadExpButton.config(bg='green')
            self.experimentPlanReady = True
        return
    
    def VOOTSD(self,data): 
        '''
        Verify Order Of Time Sensitive Data, which must be an 
        iterable of numbers like a list or tuple or vector.
        
        Return: Boolean
        V5 up to date
        '''
        testList = []
        for i in data:
            testList.append(i[0])
        testList2 = testList.copy()
        testList.sort(reverse=False)
        if testList2 == testList:
            return True
        else:
            return False
    
    def readyUpdater(self): 
        '''
        If noncam connections aka serial connections are ready,
        the camera connection is ready, and the experiment plan is loaded,
        then we are ready to go!
        
        Return: Boolean
        V5 up to date
        '''
        if self.__ncc.serialReady \
            and self.__cam.cameraLibReady \
            and self.experimentPlanReady:
            self.readyIndicator.configure(bg='green',text='Ready')
            self.readyCheckButton.configure(bg='green')
            print("Ready to go")
            return True
        print("Not ready")
        print("Serials ready:",self.__ncc.serialReady)
        print("Camera library ready:",self.__cam.cameraLibReady)
        print("Experiment plan ready:",self.experimentPlanReady)
        return False
    
    def readyText(self):
        '''
        return: Gives a message saying if each of the parts of the experiment
        are ready or not
        
        rtype: String
        V5 up to date
        '''
        if self.__cam.cameraLibReady:
            cr = 'yes'
        else:
            cr = 'no'
        if self.__ncc.serialReady:
            sr = 'yes'
        else:
            sr = 'no'
        if self.experimentPlanReady:
            epr = 'yes'
        else:
            epr = 'no'
        return 'Ready states-\n\nCamera: '+ cr \
            + '\nSerial Connections: '+ sr \
            + '\nLoaded Experiment: ' + epr

    def experimentStartDialog(self):
        '''Run the experiment based on the loaded experiment plan
        
        '''
        if self.readyUpdater():
            runOrNot = msgbox.askyesno(title='Run Experiment',
                                       message='Do you want to run an experiment?')
            if runOrNot:
                self.maxCamTime = self.cameraData[-1][0]
                self.maxPGenTime = self.PGenData[-1][0]
                self.maxVgenTime = self.VGenData[-1][0]
                self.experimentRuntime = max(self.maxCamTime,
                                             self.maxPGenTime,
                                             self.maxVgenTime)
                if not msgbox.askyesno(title='Experiment Runtime',
                                       message="The data provided in the" \
                                           + " experiment design file's last time" \
                                           + " value is at " \
                                           +str(self.experimentRuntime) \
                                           + ' seconds\nDo you want the' \
                                           + ' experiment to' \
                                           + ' have that duration?'):
                    try:
                        self.experimentRuntime = \
                        int(askstring('Experiment Runtime Dialog',
                            'Please input desired experiment duration (in seconds)'
                            ))
                    except:
                        msgbox.showerror(title='Error',
                                         message='Input must be a string')
                        return
                outFolderName = askstring("Folder creation naming dialogue",
                                          "Please input the name of the folder" \
                                          + " that all of the experiment output" \
                                          + " info will be placed into in the" \
                                          + " Experiment_Info_and_Pictures folder")
                self.outFolderPath = r"Experiment_Info_and_Pictures/" \
                                    + outFolderName
                os.mkdir(self.outFolderPath)
                self.outExpSettingsPath = self.outFolderPath \
                                          +"/experiment_settings.txt"
                copyfile(self.filename,self.outExpSettingsPath)
                
                self.antiDelay = float(self.__cam.antiDelayEntry.get())
                
                self.__ncc.updateAmpFactor()
                
                self.amp = self.__ncc.ampFactor
                
                if not self.__cam.updateGain():
                    msgbox.showerror(title='Error',
                                     message="Cannot update gain, see command line")
                    return
                if not self.__cam.updateExposure():
                    msgbox.showerror(title='Error',
                                     message="Cannot update exposure, see command line")
                    return
                if not self.__cam.updateBlackLevel():
                    msgbox.showerror(title="Error",
                                     message="Cannot update black level")
                    return
                
                self.__cam.updateGain()
                
                extraSpecsMsg = "Delay compensation = " \
                              + str(self.antiDelay) \
                              + "\nAmplification factor = " \
                              + str(self.amp) \
                              + "\nGain:" \
                              + str(self.__cam.gain) \
                              + "\nExposure:" \
                              + str(self.__cam.exposure) \
                              + "\nBlack Level:" \
                              + str(self.__cam.blackLevel) \
                              + "\nRGB Pattern Choice" \
                              + str(self.__cam.RGBPatternchoice)
                
                temp = open(self.outExpSettingsPath,"a")
                temp.write("\n"+extraSpecsMsg)
                temp.close()
                
                msgbox.showinfo(title="Extra specs",message=extraSpecsMsg)
                
                msgbox.showinfo(title='Begin',
                                message='Beginning experiment now (after ok is' \
                                + ' pressed)\nWatch experiment log file for' \
                                + ' how it went afterward.')
                
                #set em all to closed, 0V, and 0 pgen state
                if self.__ncc.ShutterOpen:
                    self.__ncc.toggleShutter()
                self.__ncc.voltageSet(0)
                self.__ncc.setPGen(-self.__ncc.pgenCoord)
                print("Starting Experiment\n========")
                try:
                    self.runExperiment()
                except:
                    temp = sys.exc_info()[0]
                    sys.stdout = self.consolePrintStdOut
                    print("Experiment failed with the following error:")
                    print(temp)
        else:
            msgbox.showwarning(title='Not ready', message=self.readyText())
        return
    
    def takePictureExp(self,
                       timeOfBurst,
                       numberOfFrames,
                       delay_,
                       frameInterval_):
        interval = max(0,frameInterval_-self.antiDelay)
        actualDelay = max(0,delay_-self.antiDelay)
        
        if self.__ncc.ShutterOpen:
            self.__cam.takePicturePython(
                self.outFolderPath,
                timeOfBurst,
                numberOfFrames,
                actualDelay,
                interval)
        else:
            self.__ncc.toggleShutter()
            self.__cam.takePicturePython(
                self.outFolderPath,
                timeOfBurst,
                numberOfFrames,
                actualDelay,
                interval)
            self.__ncc.toggleShutter()
        return

    def runExperiment(self):
        """
        :return: DESCRIPTION
        :rtype: TYPE

        """
        self.est = time.time() #est = experiment start time
        self.rttsoe = time.time() - self.est
        #rttsoe = relative time to start of experiment
        
        self.camCounter = 0
        self.PGenCounter = 0
        self.VGenCounter = 0
        self.shutterCounter = 0
        
        if not self.expDebState.get():
            sys.stdout = open(self.outFolderPath+r"/Experiment_Log_File.txt","w")
        while self.rttsoe < self.experimentRuntime+5:
            self.rttsoe = time.time() - self.est
            
            if not (self.VGenCounter == len(self.VGenData)) \
               and (self.rttsoe >= self.VGenData[self.VGenCounter][0]):
                print("Voltage altered at relative time:",self.rttsoe)
                self.__ncc.voltageSet(self.VGenData[self.VGenCounter][1])
                self.VGenCounter += 1
            
            if not (self.PGenCounter == len(self.PGenData)) \
               and (self.rttsoe >= self.PGenData[self.PGenCounter][0]):
                    print("Pressure altered at relative time:",self.rttsoe)
                    self.__ncc.setPGen(self.PGenData[self.PGenCounter][1])
                    self.PGenCounter += 1
            
            if not (self.shutterCounter == len(self.ShutterData)) \
               and (self.rttsoe >= self.ShutterData[self.shutterCounter][0]):
                    print("Shutter operation at relative time:",self.rttsoe)
                    self.__ncc.shutterSet(
                        self.ShutterData[self.shutterCounter][1]
                        )
                    self.shutterCounter += 1

            if not (self.camCounter == len(self.cameraData)) \
               and (self.rttsoe >= \
                    (self.cameraData[self.camCounter][0] - self.antiDelay)):
                    print("Picture burst started at relative time:",self.rttsoe)
                    print("Number of frames in burst:",
                          self.cameraData[self.camCounter][1])
                    print("Allocated delay before 1st pic in burst:",
                          self.cameraData[self.camCounter][2])
                    print("Interval between frames in burst:",
                          self.cameraData[self.camCounter][3])
                    self.takePictureExp(*self.cameraData[self.camCounter])
                    self.camCounter += 1

            else:
                time.sleep(.5)

        self.readyIndicator.configure(text='Experiment Complete',bg='purple')
        
        if not self.expDebState.get():
            sys.stdout.close()
            sys.stdout = self.consolePrintStdOut
        
        print("Experiment Complete")
        return

class designWindow(tkinter.Toplevel):
    '''Class to construct a window for building an experiment.
        
        implementedState: Whether or not we've implemented that this design
        window will be available to activate.
        type implementedState: Boolean.
        
        cameraFormatIN: Describes how the vector should be formatted for the
        camera channel.
        type cameraFormatIN: String.
        VGenFormatIN: Describes how the vector should be formatted for the
        VGen channel.
        type VGenFormatIN: String.
        PGenFormatIN: Describes how the vector should be formatted for the
        Pgen channel.
        PGenFormatIN: String.
        shutterFormatIN: Describes how the vector should be formatted for the
        shutter channel.
        type shutterFormatIN: String.
    '''
    
    def __init__(self,implementedState,
                 cameraFormat_,
                 VGenFormat_,
                 PgenFormat_,
                 shutterFormat_):
        '''
        :param implementedState: DESCRIPTION
        :type implementedState: TYPE
        :param cameraFormat_: DESCRIPTION
        :type cameraFormat_: TYPE
        :param VGenFormat_: DESCRIPTION
        :type VGenFormat_: TYPE
        :param PgenFormat_: DESCRIPTION
        :type PgenFormat_: TYPE
        :param shutterFormat_: DESCRIPTION
        :type shutterFormat_: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        '''

        if implementedState:
            tkinter.Toplevel.__init__(self)

            self.cameraFormat = cameraFormat_
            self.VGenFormat = VGenFormat_
            self.PGenFormat = PgenFormat_
            self.shutterFormat = shutterFormat_
            
            self.title('Design a new experiment')
            
            ''' Text input area setup '''
            textFrame = tkinter.Frame(self)
            textFrame.grid(row=1,column=0,columnspan=2,rowspan=4,padx=10,pady=5)
            
            textTitle = tkinter.Label(textFrame,text='Experimental design document:')
            textTitle.grid(row=0,column=0)
            
            self.designText = tkinter.Text(textFrame)
            
            self.designText.insert(tkinter.END,'Camera:\n')
            self.designText.mark_set('camMark',tkinter.END+'-1c')
            self.designText.mark_gravity('camMark',tkinter.LEFT)
            
            self.designText.insert(tkinter.END,';\nPGen:\n')
            self.designText.mark_set('PGenMark',tkinter.END+'-1c')
            self.designText.mark_gravity('PGenMark',tkinter.LEFT)
            
            self.designText.insert(tkinter.END,';\nVGen:\n')
            self.designText.mark_set('VGenMark',tkinter.END+'-1c')
            self.designText.mark_gravity('VGenMark',tkinter.LEFT)
            
            self.designText.insert(tkinter.END,';\nShutter:\n')
            self.designText.mark_set('ShutterMark',tkinter.END+'-1c')
            self.designText.mark_gravity('ShutterMark',tkinter.LEFT)
            
            self.designText.insert(tkinter.END,';')
            
            self.designText.mark_gravity('camMark',tkinter.RIGHT)
            self.designText.mark_gravity('PGenMark',tkinter.RIGHT)
            self.designText.mark_gravity('VGenMark',tkinter.RIGHT)
            self.designText.mark_gravity('ShutterMark',tkinter.RIGHT)
            
            self.designText.grid(row=1,column=0,columnspan=2,rowspan=3,padx=10,pady=5)
            ''' '''
           
            ''' File interaction stuff and exiting stuff'''
            saveAndQuitFrame = tkinter.Frame(self,borderwidth=1,relief='solid')
            saveAndQuitFrame.grid(row=0,column=0)
            
            sortButton = tkinter.Button(saveAndQuitFrame,text='Reformat Data into Format',command=self.reformatDesign)
            sortButton.grid(row=0,column=0)
            
            saveButton = tkinter.Button(saveAndQuitFrame,text='Save to file',command=self.saveDesign)
            saveButton.grid(row=0,column=1)
            
            closeDesignScreenButton = tkinter.Button(saveAndQuitFrame,text='Close Design Window',command=self.quitDesign)
            closeDesignScreenButton.grid(row=0,column=2)
            ''' '''
            
            ''' Notebook '''
            from tkinter import ttk
            insertNotebookPanel = ttk.Notebook(self)       
            insertNotebookPanel.grid(row=2,column=2,padx=10)
            
            cameraTab = ttk.Frame(insertNotebookPanel)
            cameraLabel = tkinter.Message(cameraTab,text='The camera information is grouped according to: Time, Number of Frames, Delay, and Interval between frames, and is an ordered quartet')
            cameraLabel.grid(row=0,column=0)
            cameraInsertButton = tkinter.Button(cameraTab,text='Add new sets',command=self.addNewCameraSets)
            cameraInsertButton.grid(row=0,column=1)
            insertNotebookPanel.add(cameraTab,text='Camera')
            
            PGenTab = ttk.Frame(insertNotebookPanel)
            PGenLabel = tkinter.Message(PGenTab,
                                        text='The PGen information is grouped according to: Time and Relative coordinate to the origin (in number of PGen units (where 0.1 is a full step), where the origin is manually calibrated with the buttons or by physically moving the stepper), and is an ordered pair'
                                        )
            PGenLabel.grid(row=0,column=0)
            PGenInsertButton = tkinter.Button(PGenTab,text='Add new sets',command=self.addNewPGenSets)
            PGenInsertButton.grid(row=0,column=1)
            insertNotebookPanel.add(PGenTab,text='PGen')
            
            VGenTab = ttk.Frame(insertNotebookPanel)
            VGenLabel = tkinter.Message(VGenTab,text='The VGen information is grouped according to: Time and Voltage, and is an ordered pair')
            VGenLabel.grid(row=0,column=0)
            VGenInsertButton = tkinter.Button(VGenTab,text='Add new sets',command=self.addNewVGenSets)
            VGenInsertButton.grid(row=0,column=1)
            insertNotebookPanel.add(VGenTab,text='VGen')
            
            ShutterTab = ttk.Frame(insertNotebookPanel)
            ShutterLabel = tkinter.Message(ShutterTab,text='The shutter information is grouped according to: Time and shutter state (1 = open, 0 = closed), and is an ordered pair')
            ShutterLabel.grid(row=0,column=0)
            ShutterInsertButton = tkinter.Button(ShutterTab,text='Add new sets',command=self.addNewShutterSets)
            ShutterInsertButton.grid(row=0,column=1)
            insertNotebookPanel.add(ShutterTab,text='Shutter')
            ''' '''
            
            ''' Asterisk replacement frame (arf) '''
            arf = tkinter.Frame(self,borderwidth=1,relief='solid')
            arf.grid(row=3,column=2,padx=10)
            
            #Asterisk Replacement Label
            arl = tkinter.Label(arf,text='Asterisk Replacement')
            arl.grid(row=0,column=0)
            
            #Replace Each Asterisk With Zeroes Button
            reawzb = tkinter.Button(arf,text='Replace all with zeroes',command=self.asterisksToZeroes)
            reawzb.grid(row=1,column=0,pady=5,padx=5)
            
            #Asterisk Finder Button
            afb = tkinter.Button(arf,text='Find next',command=self.findNextAsterisk)
            afb.grid(row=2,column=0,pady=5,padx=5)
            ''' '''
        
        else:
            msgbox.showwarning(title='Warning',message='Unimplemented feature, this button does nothing for now.')
            return
    
    def addNewShutterSets(self):
        ''' 
        Add a number of sets of shutter data.
        
        Return: None.
        '''
        self.addNewSetGeneric('shutter')
        return
    
    def asterisksToZeroes(self):
        '''
        Convert all asterisks in the experiment design dialogue with zeros.
        
        Return:None.
        '''
        texts = self.designText.get(0.0,tkinter.END)
        while '*' in texts:
            tempIndex = self.designText.search('*',0.0)
            self.designText.delete(tempIndex)
            self.designText.insert(tempIndex,'0')
            texts = self.designText.get(0.0,tkinter.END)
        return
    
    def findNextAsterisk(self):
        '''
        Set cursor in design window to the location of the next asterisk
        after the cursor.
        
        Return: None.
        '''
        texts = self.designText.get(tkinter.INSERT,tkinter.END)
        if '*' in texts:
            tempIndex = self.designText.search('*',tkinter.INSERT)
            self.designText.mark_set('insert',tempIndex)
        else:
            msgbox.showinfo(master=self,
                            title='None found',
                            message='No instances of * were found after the cursor')
        return
   
    def quitDesign(self):
        ''' 
        Warns the user and gives them a chance to back out before closing
        design window.
        
        Return: None.
        '''
        if msgbox.askokcancel(parent=self,
                              title='Quit',
                              message='Are you sure you want to exit the experiment design without saving?',
                              default='cancel'):
            self.destroy()
        return
    
    def saveDesign(self):
        '''
        Creates a file save dialogue that will be used to save the contents
        of the design window.
        
        Return: None (saves a file)
        '''
        try:
            designSaveInfo = self.designText.get(0.0,tkinter.END)
            saveFile = fileDialog.asksaveasfile(mode='w',
                                                defaultextension='.txt',
                                                parent=self)
            if saveFile == None:
                return
            saveFile.write(designSaveInfo)
            saveFile.close()
        except:
            msgbox.showerror(parent=self,
                             title='An exception has occured',
                             message=str(sys.exc_info()[0]))
            return
        msgbox.showinfo(parent=self,
                        title='Success',
                        message='File successfully saved')
        return
    
    def addNewSetGeneric(self,setType): #setType is a string
        """
        Creates a new set of data in the design window of a given type of data.
        
        setType: Which data we're generating sets for.
        type setType: String.
        """
        answer = msgbox.askyesno(master=self,
                title='Possible Shortcut',
                message='Is there an interval pattern to the times for the sets?')
        if setType == 'camera':
            mark = 'camMark'
            Format = self.cameraFormat
        elif setType == 'VGen':
            mark = 'VGenMark'
            Format = self.VGenFormat
        elif setType == 'PGen':
            mark = 'PGenMark'
            Format = self.PGenFormat
        elif setType == 'shutter':
            mark = 'ShutterMark'
            Format = self.shutterFormat
        try:
            if answer:
                start = int(askstring('Start','Starting time value? (in s)'))
                stop = int(askstring('Stop','Stopping time value? (in s)'))
                interval = int(askstring('Step',
                           'Interval between '+ setType \
                            + ' sets? (Please note that all numbers will be ' \
                            + 'rounded down if this results in decimals)'))
                times = np.arange(start,stop,interval).astype(int).astype(str)
                if not(str(stop) in times):
                    times = np.append(times,str(stop))
                msgbox.showinfo(parent=self,
                    title='Times',
                    message='These are the times for the experiment:\n' \
                    +str(times))
            else:
                number = int(askstring('',
                                       'Number of sets you would like to add'))
                times = np.core.defchararray.array('*'*number,itemsize=1)
        except:
            msgbox.showerror(parent=self,
                title='Error',
                message='Likely inputted value that is not a number. Specific' \
                ' error:\n'+str(sys.exc_info()[0]))
        for i in range(len(times)):
            self.designText.insert(mark,'('+times[i]+Format+')')
        return   

    def addNewCameraSets(self):
        ''' 
        Add a number of sets of camera data.
        
        Return: None.
        '''
        self.addNewSetGeneric('camera')
        return
    
    def addNewPGenSets(self):
        ''' 
        Add a number of sets of PGen data.
        
        Return: None.
        '''
        self.addNewSetGeneric('PGen')
        return
    
    def addNewVGenSets(self):
        ''' 
        Add a number of sets of VGen data.
        
        Return: None.
        '''
        self.addNewSetGeneric('VGen')
        return

    def reformatDesign(self):
        '''
        Reorders all the data in the experiment design window into a form that
        the loadExperiment function can parse. Will try to tell the user what's
        wrong with the data formatting if it can.
        
        return: NONE (reorders data in place).
        '''
        raw = self.designText.get(0.0,tkinter.END)
        
        sortedCamera = list(self.fileDataSearch('Camera:',raw))
        
        #Checks that the camera data is correctly formatted
        if sortedCamera[0] == -1:
            msgbox.showerror(title='Error',
                message='File data search encountered the following error:\n' \
                +sortedCamera[1],
                parent=self)
            return
        sortedCamera.sort()
        
        for b in range(len(sortedCamera)):
            sortedCamera[b] = list(sortedCamera[b])
            sortedCamera[b][1] = int(sortedCamera[b][1])
            sortedCamera[b] = tuple(sortedCamera[b])
        
        sortedPGen = list(self.fileDataSearch('PGen:',raw))
        
        if sortedPGen[0] == -1:
            msgbox.showerror(title='Error',message='File data search encountered the following error:\n'+sortedPGen[1],parent=self)
            return
        sortedPGen.sort()
        
        sortedVGen = list(self.fileDataSearch('VGen:',raw))
        
        if sortedVGen[0] == -1:
            msgbox.showerror(title='Error',message='File data search encountered the following error:\n'+sortedVGen[1],parent=self)
            return
        sortedVGen.sort()
        
        sortedShutter = list(self.fileDataSearch('Shutter:', raw))
        
        if sortedShutter[0] == -1:
            msgbox.showerror(title='Error',message='File data search encountered the following error:\n'+sortedShutter[1],parent=self)
            return
        sortedShutter.sort()
        
        for a in range(len(sortedShutter)):
            sortedShutter[a] = list(sortedShutter[a])
            sortedShutter[a][1] = int(sortedShutter[a][1])
            sortedShutter[a] = tuple(sortedShutter[a])
        
        #wipes the window
        self.designText.delete(0.0,tkinter.END)
        
        #puts in the newly reformmated data (does not retain any miscellaneous
        #text)
        self.designText.insert(tkinter.END,'Camera:')
        for i in sortedCamera:
            self.designText.insert(tkinter.END,str(i))
            if i != sortedCamera[-1]:
                self.designText.insert(tkinter.END,',')
        self.designText.insert(tkinter.END,'\n')
        
        self.designText.mark_set('camMark',tkinter.END+'-1c')
        self.designText.mark_gravity('camMark',tkinter.LEFT)
            
        self.designText.insert(tkinter.END,';\nPGen:')
        for j in sortedPGen:
            self.designText.insert(tkinter.END,str(j))
            if j != sortedPGen[-1]:
                self.designText.insert(tkinter.END,',')
        self.designText.insert(tkinter.END,'\n')
        
        self.designText.mark_set('PGenMark',tkinter.END+'-1c')
        self.designText.mark_gravity('PGenMark',tkinter.LEFT)
            
        self.designText.insert(tkinter.END,';\nVGen:')
        for k in sortedVGen:
            self.designText.insert(tkinter.END,str(k))
            if k != sortedVGen[-1]:
                self.designText.insert(tkinter.END,',')
        self.designText.insert(tkinter.END,'\n')
        
        self.designText.mark_set('VGenMark',tkinter.END+'-1c')
        self.designText.mark_gravity('VGenMark',tkinter.LEFT)
        
        self.designText.insert(tkinter.END,';\nShutter:')
        for m in sortedShutter:
            self.designText.insert(tkinter.END,str(m))
            if m != sortedVGen[-1]:
                self.designText.insert(tkinter.END,',')
        self.designText.insert(tkinter.END,'\n')
        
        self.designText.mark_set('ShutterMark',tkinter.END+'-1c')
        self.designText.mark_gravity('ShutterMark',tkinter.LEFT)
            
        self.designText.insert(tkinter.END,';')
            
        self.designText.mark_gravity('camMark',tkinter.RIGHT)
        self.designText.mark_gravity('PGenMark',tkinter.RIGHT)
        self.designText.mark_gravity('VGenMark',tkinter.RIGHT)
        self.designText.mark_gravity('ShutterMark',tkinter.RIGHT)
        return

    def fileDataSearch(self,startingPhrase,searchedString,endingCharacter=';'):
        
        '''
        startingPhrase is a string that indicates what is the start of a data entry
        
        I've intentionally coded it open so we can add more entries if necessary so 
        we can increase the number of things the code manipulates later
        
        searchedString is the string we are looking inside of for startingPhrase
        
        endingCharacter is what tells us that that data set terminates it defaults 
        to semicolon but if someone wants to change it, be my guest, just pass it 
        an argument to replace it
        '''
        
        LSP = len(startingPhrase) #just shorthand for Length of Starting Phrase
        for check in range(len(searchedString)-LSP): 
            #looking through searchedString for startingPhrase
            if searchedString[check:LSP+check] == startingPhrase: #we find a match
                endChar = '0'
                for i in range(check,len(searchedString)):
                    endChar = searchedString[i]
                    if endChar == endingCharacter: #looking for the end of the phrase
                        foundPhrase = searchedString[check:i]
                        phraseEndNumber = i
                        for j in range(len(foundPhrase)):
                            #seperating each set of data in (each set of parentheses) into a list
                            if foundPhrase[j] =='(': #found a new data set
                                data = foundPhrase[j:phraseEndNumber]
                                ldtc = len(data)
                                ptl = []
                                for i in range(ldtc):
                                    if data[i] == '(':
                                        j = i
                                        while data[j] != ')': 
                                            #search till the end of the data set
                                            j += 1
                                            if j > ldtc:
                                                return -1,'error, no closing parentheses',-1
                                        try:
                                            bit = data[i+1:j] 
                                            #this is the data inside the set
                                            temp = bit.split(',') 
                                            #we take out the commas and make the set a list
                                            for k in range(len(temp)):
                                                temp[k] = float(temp[k]) 
                                                #we convert everything to numbers
                                        except:
                                            return -1,'error, non digit character found in data',-1
                                        ptl.append(tuple(temp))
                                        '''we add append the list of
                                        that one data set as a tuple to the ultimate list
                                        containing all the data sets in this phrase'''
                                        
                                return tuple(ptl) 
                                '''we return the list containing all the data sets 
                                of this phrase, as a tuple'''
                                
                        return -1,'no parentheses starts',-1           
                return -1,'could not find end',-1
        return -1,'could not find beginning',-1  