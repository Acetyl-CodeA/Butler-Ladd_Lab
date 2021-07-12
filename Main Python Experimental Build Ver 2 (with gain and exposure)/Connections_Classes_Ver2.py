# -*- coding: utf-8 -*-
"""
All connections classes
"""
import tkinter
import tkinter.messagebox as msgbox
import sys
import ctypes as ct
import serial
import pyvisa as pv
import os
import subprocess
import tkinter.filedialog as fileDialog

class camera(object):
    '''
    Object that contains all of the information and connections related to
    the camera (not the shutter, that's in allNonCamConnectClass objects).
        
    master_: Main GUI frame.
    type master_: Tkinter.tk() object

    '''
    
    def __init__(self,master_):

        self.master = master_
        self.camFrame = tkinter.Frame(self.master,relief="solid",borderwidth=1)
        
        self.camFrameLabel = tkinter.Label(self.camFrame,text='Camera')
        self.camFrameLabel.grid(row=0,column=0)
        
        self.picCanvas = tkinter.Canvas(self.master, 
                                        width = 1392//4, 
                                        height = 1040//4)
        self.picCanvas.grid(row=1,column=1)
        
        self.setupLibButton = tkinter.Button(self.camFrame,
                                        command=self.alexLibrarySetup,
                                        text='Set up camera library',
                                        bg='red')
        self.setupLibButton.grid(row=0,column=1,pady=3,padx=3)
        
        self.gainEntryLabel = tkinter.Label(self.camFrame,text="Gain:")
        self.gainEntryLabel.grid(row=1,column=0)
        
        self.defaultGainEntryVar = tkinter.StringVar()
        self.defaultGainEntryVar.set("39")
        self.gainEntry = tkinter.Entry(self.camFrame,textvariable=self.defaultGainEntryVar)
        self.gainEntry.grid(row=1,column=1)
        
        self.exposureEntryLabel = tkinter.Label(self.camFrame,text="Exposure (microseconds):")
        self.exposureEntryLabel.grid(row=2,column=0)
        
        self.defaultExposureEntryVar = tkinter.StringVar()
        self.defaultExposureEntryVar.set("1e5")
        self.exposureEntry = tkinter.Entry(self.camFrame,textvariable=self.defaultExposureEntryVar)
        self.exposureEntry.grid(row=2,column=1)
        
        self.processImagesButton = tkinter.Button(self.camFrame,
                                           command=self.processFolderOfImages,
                                           text="Process a folder of images")
        self.processImagesButton.grid(row=6,column=0,pady=3,padx=3,columnspan=2)
        
        self.antiDelayLabel = tkinter.Label(self.camFrame,text="Delay of camera in seconds (will queue up image sooner to counter it):")
        self.antiDelayLabel.grid(row=3,column=0,columnspan=2)
        
        self.defaultAntiDelayEntryVar = tkinter.StringVar()
        self.defaultAntiDelayEntryVar.set("0.6")
        self.antiDelayEntry = tkinter.Entry(self.camFrame,textvariable=self.defaultAntiDelayEntryVar)
        self.antiDelayEntry.grid(row=4,column=0,columnspan=2)
        
        #temporarily disabled, need to add a file dialog
        '''
        self.takePictureButton = tkinter.Button(self.camFrame,
                                           command=self.takePicturePython,
                                           text="Take picture")
        self.takePictureButton.grid(row=2,column=0,pady=3,padx=3)
        '''
        
        self.takePicButtonUpdateCanvas = tkinter.Button(self.camFrame,
                                          command = self.takePicAndUpdateCanvas,
                                          text="Take picture and update preview")
        self.takePicButtonUpdateCanvas.grid(row=5,column=0,pady=3,padx=3,columnspan=2)
        

        
        self.cameraLibReady = False
        return
    
    def processFolderOfImages(self):
        '''
        Creates a folder of postprocessed images from a
        folder of preprocessed images. [Uses an executable to do via the
        self.picProcess function]
        
        return: None 

        '''
        imgFolder = fileDialog.askdirectory()
        files = os.listdir(imgFolder)
        print(files)
        outDir = imgFolder + r"/processedImages"
        os.mkdir(outDir)
        for i in files:
            if ("picNumber" in i) and (".txt" in i):
                self.picProcess(imgFolder + r"/" + i,outDir + r"/" + i[:-4] + ".png")
        print("done processing")
        return
    
    def updateGain(self,ctypeType=True):
        #boolean output is whether we succeeded in updating gain
        try:
            self.gainTry = float(self.gainEntry.get())
        except:
            print("Invalid, cannot convert to float")
            return False
        if self.gainTry < 0.817:
            print("Gain is below minimum of 0.817")
            return False
        elif self.gainTry > 39:
            print("Gain is above maximum of 39")
            return False
        else:
            if ctypeType:
                self.gain = ct.c_double(self.gainTry)
                return True
            else:
                self.gain = self.gainTry
                return True
    
    def updateExposure(self,ctypeType=True):
        #boolean output is whether we succeeded in updating exposure
        try:
            self.exposureTry = float(self.exposureEntry.get())
        except:
            print("Invalid, cannot convert to float")
            return False
        if self.exposureTry < 1:
            print("Exposure is below minimum of 1")
            return False
        elif self.exposureTry > 1.074e9:
            print("Exposure is above maximum of 1.074e9")
            return False
        else:
            if ctypeType:
                self.exposure = ct.c_double(self.exposureTry)
                return True
            else:
                self.exposure = self.exposureTry
                return True
    
    def takePicAndUpdateCanvas(self):
        '''
        Self-explanatory. Take a picture, place the unprocessed file in the 
        temp folder, processes it and places the folder in the temp folder,
        then displays the photo in the GUI.
        
        :return: None

        '''
        if self.cameraLibReady:
            try:
                if not self.updateExposure():
                    msgbox.showerror(title='Error',message="Cannot update exposure, see command line")
                    return
                if not self.updateGain():
                    msgbox.showerror(title='Error',message="Cannot update gain, see command line")
                    return
                self.takePic(self.arrayOfErrors,self.camOutput,self.gain,self.exposure)
                self.picFileWrite(self.tempPicTextFname)
                self.picProcess(self.tempPicTextFname,self.tempPicPngOutname)
                self.displayPicture(self.tempPicPngOutname)
                self.master.update()
                print("succesfully updated canvas")
            except:
                 msgbox.showerror(title='An exception has occured',message= 'Error ' 
                                 +'setting up camera, make sure that:\n'
                                 +"1)It's on\n"
                                 +"2)Connected\n3)You have the "
                                 +"driver in this folder\n"
                                 +"4)You have the Alex library in this folder"
                                 +"\nError message:\n" + str(sys.exc_info()[0]))
        else:
            msgbox.showerror(title='Error',message="Camera library not set up yet")
        return

    def alexLibrarySetup(self):
        """
        Sets up the C++ wrapper library for the C language SDK provided by the
        camera manufacturer. Also takes a picture and displays it to make sure
        it's all functioning correctly. Once this library is loaded, we can
        take pictures using other functions.
        
        return: None

        """
        try:
            self.alib = ct.CDLL("QCamApi_AlexTakeAPic_Ver2.dll")
            self.frameSize = self.alib.PostProcessedFrameSize()
            
            ULONG_6 = ct.c_ulong * 6
            self.arrayOfErrors = ULONG_6()
            
            self.camOutput = ct.create_string_buffer(self.frameSize)
            
            self.takePic = self.alib.TakePicture
            
            if not self.updateGain():
                    msgbox.showerror(title='Error',message="Cannot update gain, see command line")
                    return
            if not self.updateExposure():
                    msgbox.showerror(title='Error',message="Cannot update exposure, see command line")
                    return
            
            self.takePic.argtypes = ULONG_6, ct.c_char_p,  ct.c_double, ct.c_double
            self.takePic(self.arrayOfErrors,self.camOutput, self.gain,self.exposure)
            
            #unimplemented, convert error codes to what the error is
            #self.errorsList,self.errorCategory = [],[]
            
            print("Error Messages (0 means ran without issue, -1 means it crashed before this could be initialized)")
            print("Load driver:",self.arrayOfErrors[0])
            print("Load up list of cameras:",self.arrayOfErrors[1])
            print("Open the camera:",self.arrayOfErrors[2])
            print("Obtain camera info:",self.arrayOfErrors[3])
            print("Grab frame:",self.arrayOfErrors[4])
            print("Close camera:",self.arrayOfErrors[5])
            
            if not (self.arrayOfErrors[0] or \
                    self.arrayOfErrors[1] or \
                    self.arrayOfErrors[2] or \
                    self.arrayOfErrors[3] or \
                    self.arrayOfErrors[4] or \
                    self.arrayOfErrors[5]):
                #print('passed conditional')
                self.tempPicTextFname = r"Temporary Image Files for GUI/rawImageForTest.txt"
                #print("passed file naming")
                self.picFileWrite(self.tempPicTextFname)
                self.tempPicPngOutname = r"Temporary Image Files for GUI/testImage.png"
                self.picProcess(self.tempPicTextFname,self.tempPicPngOutname)
                #print("passed file processing")
                self.displayPicture(self.tempPicPngOutname)
                self.cameraLibReady = True
                self.setupLibButton.configure(bg="green")
                return
            print("There was an error, check the command line for error messages from the library")
        except:
            msgbox.showerror(title='An exception has occured',message= 'Error ' 
                                 +'setting up camera, make sure that:\n'
                                 +"1)It's on\n"
                                 +"2)Connected\n3)You have the "
                                 +"driver in this folder\n"
                                 +"4)You have the Alex library in this folder"
                                 +"\nError message:\n" + str(sys.exc_info()[0]))
                #shows both a generic suggestion and the specific error thrown
        return
        
    def picFileWrite(self,destPath):
        '''
        Write the data in the self.camOutput ctypes array into a text file in
        destPath.
        
        destPath: Path including extension of txt file to write
        type destPath: String
        
        return: NONE
        '''
        
        if os.path.exists(destPath):
            os.remove(destPath)
        f = open(destPath,"ab")
        
        for i in range(self.frameSize):
            f.write(self.camOutput[i])
        
        f.close()
        return
    
    def picProcess(self,inputTxtPath,outPicPath):
        '''
        Processes data in a txt file that contains unprocessed camera output
        data into a png using the Image_Processor_ARGV executable generated
        from 64-bit Python imageio/rawpy libraries. If you do not have this
        executable in a folder with all its requisite libraries, this function
        will fail.
        
        inputTxtPath: Path of txt file to process, must include the
        extension. It should work for other file types, but this was designed
        with txt in mind.
        type inputTxtPath: String.
        
        outPicPath: Path of the picture file to produce, must include the
        extension. This one is more finnicky about the file types it will 
        permit. The file extensions png and tiff are probably fine, just know 
        that this was written with png in mind.
        
        type outPicPath: String.
        
        return: None.
        '''
        exePath = r"Image_Processor_ARGV/Image_Processor_ARGV.exe"
        args = exePath + ' "' + inputTxtPath + '" "' + outPicPath + '"'
        FNULL = open(os.devnull, 'w')
        #use this ^ if you want to suppress output to stdout from the subprocess
        subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
        return
    
    def displayPicture(self,picPath):
        '''
        Constructs a canvas object in the main tkinter object (canvases are for
        displaying images in tkinter). It then will take an image file and
        display it in the canvas. The weird dimensions are to preserve the
        aspect ratio of the picture.
        
        picPath: Path including file extension of the image to be displayed.
        This was designed to use .png files, but others may work. Other 
        extensions may work, but you may need Pillow to use them.
        type picPath: String.
        
        Return: None.
        '''
        self.img = tkinter.PhotoImage(file=picPath)      
        self.picCanvas.create_image(20,20, anchor=tkinter.NW, image=self.img)  
        return
    
    def takePicturePython(self,txtOutPath):
        '''
        Takes a picture using the C++ wrapper library (via ctypes) and then
        writes the resultant camOutput to a txt file.
        
        param txtOutPath: Tells you what the path for the output
        text file will be. Does NOT convert the image for you.
        
        Return: None.
        '''
        if self.cameraLibReady:
            self.takePic(self.arrayOfErrors,self.camOutput,self.gain,self.exposure)
            self.picFileWrite(txtOutPath)
        else:
            msgbox.showerror("Not Ready","Library is not ready to take picture")
        return

class allNonCamConnectClass(object):
    '''
    Object used for controlling the VGen, PGen, and Shutter. Manages those
    connections and also the GUI frame that relates to all of their connections.
    
    param master_: Main tkinter.tk() object that everything in the GUI is
    based on
    
    type master_: tkinter.tk() object
    
    '''
    def __init__(self,master_):

        self.shutterReady = False
        self.pgenReady = False
        self.serialReady = False
        self.master = master_
        
        self.pgenCoord = 0
        
        self.cif = tkinter.Frame(self.master,relief='solid',borderwidth=1)
        #cif = Comport inputs frame
        self.cifTitle = tkinter.Label(self.cif,text='Input Com Port Numbers:')
        self.cifTitle.grid(row=0,column=1)
        
        self.scb = tkinter.Button(self.cif,command=self.InitializeSerials,text='Initialize Serial Connections',borderwidth=1,relief='raised',bg='red')
        #scb = Serial Connect Button
        self.scb.grid(row=0,column=2,padx=3,pady=3,columnspan=4)
        
        self.cifShutterLabel = tkinter.Label(self.cif,text='Shutter:')
        self.cifShutterLabel.grid(row=1,column=0)
        
        self.defaultShutterEntry = tkinter.StringVar()
        self.defaultShutterEntry.set('5')
        self.shutterEntry = tkinter.Entry(self.cif,textvariable=self.defaultShutterEntry)
        self.shutterEntry.grid(row=1,column=1)
        
        self.cifPgenLabel = tkinter.Label(self.cif,text='Pgen:')
        self.cifPgenLabel.grid(row=3,column=0)
        
        self.defaultPGenEntry = tkinter.StringVar()
        self.defaultPGenEntry.set('6')
        self.PgenEntry = tkinter.Entry(self.cif,textvariable=self.defaultPGenEntry)
        self.PgenEntry.grid(row=3,column=1)
        
        self.ShutterToggleButton = tkinter.Button(self.cif,command=self.toggleShutter,text='Toggle Shutter',borderwidth=1,relief='raised',bg='red')
        self.ShutterToggleButton.grid(row=1,column=2,columnspan=4)
        
        self.voltageSetEntry = tkinter.Entry(self.cif)
        self.voltageSetEntry.grid(row=6,column=1)
        
        self.voltageSetButton = tkinter.Button(self.cif,command=self.buttonVoltageSet,text='Set Voltage Level',borderwidth=1,relief='raised',bg='red')
        self.voltageSetButton.grid(row=6,column=0)
        
        self.PgenUp1Button = tkinter.Button(self.cif,command=lambda: self.calibrationMvmt(self.P_up1),text='Up 1',borderwidth=1,relief='raised',bg='red')
        self.PgenUp1Button.grid(row=3,column=2,padx=2)
        
        self.PgenUp2Button = tkinter.Button(self.cif,command=lambda: self.calibrationMvmt(self.P_up2),text='Up 2',borderwidth=1,relief='raised',bg='red')
        self.PgenUp2Button.grid(row=3,column=3,padx=2)
        
        self.PgenDown1Button = tkinter.Button(self.cif,command=lambda: self.calibrationMvmt(self.P_down1),text='Down 1',borderwidth=1,relief='raised',bg='red')
        self.PgenDown1Button.grid(row=3,column=4,padx=2)
        
        self.PgenDown2Button = tkinter.Button(self.cif,command=lambda: self.calibrationMvmt(self.P_down2),text='Down 2',borderwidth=1,relief='raised',bg='red')
        self.PgenDown2Button.grid(row=3,column=5,padx=2)
        
        self.ampLabel = tkinter.Label(self.cif,text="Amplification factor:")
        self.ampLabel.grid(row=5,column=0)
        
        self.defaultampEntry = tkinter.StringVar()
        self.defaultampEntry.set('400')
        self.ampEntry = tkinter.Entry(self.cif,textvariable=self.defaultampEntry)
        self.ampEntry.grid(row=5,column=1)
        
        return

    def shutterSet(self,state):
        '''
        
        state: Sets the shutter to a specific state. If it's currently that
        state, it will do nothing.
        
        type state: Boolean. 1 is open, 0 is closed.
        
        return: None.

        '''
        if state != self.ShutterOpen:
            self.toggleShutter()
        return

    def buttonVoltageSet(self):
        '''
        Sets the voltage to the voltage specified in the voltage entry box.
        Uses the self.voltageSet method to do so after updating the amplification
        factor.
        
        return: None.

        '''
        self.updateAmpFactor()
        v = self.voltageSetEntry.get()
        self.voltageSet(v)
        return

    def updateAmpFactor(self):
        """
        Checks what the amplification factor in the text entry box is and
        updates accordingly.
        
        return: None (alters self.ampEntry attribute in place)

        """
        self.ampFactor = float(self.ampEntry.get())
        return

    def voltageSet(self,inputVoltage):
        '''
        Sets the voltage generator's voltage to inputVoltage/self.ampFactor.
        Does NOT update ampFactor. We divide because if we have 10 V and an
        amp factor of 10, the resultant voltage in the channel will be 100 V.
        
        inputVoltage: Voltage we want the channel to experience.
        type inputVoltage: String (expects it to be convertable to a float).
        
        return: None.

        '''
        try:
            v = float(inputVoltage)/self.ampFactor
            self.VGen.write('APPL:DC DEF,DEF,'+str(v))
        except:
            msgbox.showerror(title='An exception has occured',message= 'Error setting up the serial connections, check that the values in entry match the actual connected values\nError message:\n' + str(sys.exc_info()[0]))
            msgbox.showerror(message='Check that the value in the debug voltage entry set box is a float')
        return
    
    def setPGen(self,signedPosition):
        '''
        Sets the stepper motor location to a specific coordinate relative to
        the origin we have specified using the buttons or by manually moving it.
        Uses the P_up2(), P_up1(), P_down2(), and P_down1() methods to do so.
        
        signedPosition: What coordinate we want the stepper to move to. If it's
        positive, we go up. If it's negative, we go down.
        
        signedPosition: Float.
        
        return: None.

        '''
        neededMvmt = signedPosition - self.pgenCoord
        asd = abs(neededMvmt)
        
        noQuarterStep = round(asd/.025)
        remainder = asd - .025 * noQuarterStep
        noHundredthStep = round(remainder/.001)
        
        if round(noHundredthStep*.001+noQuarterStep*.025,5) != asd:
            print("Error, can't do that with current step sizes")
        elif neededMvmt > 0:
            for i in range(noQuarterStep):
                self.P_up2()
            for j in range(noHundredthStep):
                self.P_up1()
        elif neededMvmt < 0:
            for i in range(noQuarterStep):
                self.P_down2()
            for j in range(noHundredthStep):
                self.P_down1()
        else:
            print("Set PGen of 0 does nothing as the setting is relative movement each time")
        return
        
        
        return

    def get_inputs(self):
        '''
        Checks current state of serial entries in GUI.
        
        return: Shutter entry COM port number, VGen entry address,
        Pgen entry COM port number
        rtype: Tuple

        '''
        return (self.shutterEntry.get(), self.PgenEntry.get())
    
    def InitializeSerials(self):
        '''
        Sets up all the serial connections as attributes of the 
        allNonCamConnect class instance. The serial connections are: voltage
        generator (specifically, a VISA connection), shutter motor (Arduino
        UNO COM port connection), and stepper motor (Arduino Leonardo COM port
        connection). It will try to set up all libraries and will yield error
        messages to try to help the user fix any issues setting up.
        
        Return: None.
        '''
        
        Shutterval, Pgenval = self.get_inputs()
        '''com port that shutter is connected to, which
        we obtain by user input into the entry next to Shutter:'''
        
        temp_msg_string = 'The following are the serial connections and their corresponding ports:\n'\
        + 'Shutter: ' + Shutterval + '\nPgen: ' + Pgenval
        #confirms with the user that they inputted the right information
        
        validate = msgbox.askyesno(message= temp_msg_string + '\nIs this information correct?')
        
        if validate:
            try:
                '''make the 3 serial connection objects, which we will use later to 
                talk to the arduino'''
                self.Shutter = serial.Serial(port='com'+Shutterval,baudrate=9600)
                self.ShutterOpen = msgbox.askyesno(message='Is shutter open right now?')
                #msgbox.showinfo(message='Maybe exit out of the interface, press the reset button on the leonardo board, and then come back')
                shutterInitialize = self.Shutter.read_until()
                if shutterInitialize == b'Motor shield DC motor Test:\r\n':
                    msgbox.showinfo(message='Serial connection with shutter motor successfully opened')
                    self.ShutterToggleButton.configure(bg='green')
                    self.shutterReady = True
                    self.toggleShutter(), self.toggleShutter()
                else:
                    msgbox.showerror(message='The shutter motor failed to say its doing the motor shield dc motor test. It says this when it boots up successfully so there may be an error')
                
                self.Pgen = serial.Serial(port='com'+Pgenval,baudrate=9600)
                msgbox.showinfo(message='Pressure generator stepper motor serial connection successfully opened')
                self.pgenReady = True
                
                self.PgenDown1Button.configure(bg='green')
                self.PgenDown2Button.configure(bg='green')
                self.PgenUp1Button.configure(bg='green')
                self.PgenUp2Button.configure(bg='green')
                
                self.rm = pv.ResourceManager()
                self.resources = self.rm.list_resources()
                self.VGen = self.rm.open_resource(self.resources[0])
                self.vgenid = self.VGen.query('*IDN?')
                msgbox.showinfo(message='Voltage generator id number: '+self.vgenid+'\n successfully connected')
                
                
                msgbox.showinfo(title='Success',message='Shutter, Vgen, and Pgen successfully set up')
                self.scb.configure(bg='green')
                self.voltageSetButton.configure(bg='green')
                
                self.serialReady = True
                #readyUpdater() 
                '''checks what is ready, and if the 3 things are ready, 
                lights up the experiment readiness button'''
                self.scb.configure(bg='green')
            except:
                msgbox.showerror(title='An exception has occured',message= 'Error setting up the serial connections, check that the values in entry match the actual connected values\nError message:\n' + str(sys.exc_info()[0]))
                #shows both a generic suggestion and the specific error thrown
        return
        
    def toggleShutter(self):
        '''
        Switches the state of the shutter from open to closed or vice versa.
        
        return: None.

        '''
        if self.shutterReady == False:
            msgbox.showerror(title='Error',message='Shutter not ready')
            return
        if self.ShutterOpen:
            self.Shutter.write(b'2')
            self.ShutterOpen = False
        else:
            self.Shutter.write(b'1')
            self.ShutterOpen = True
        tempRead = self.Shutter.read_until()
        if tempRead == b'forward\r\n':
            print('Shutter opened')
        elif tempRead == b'Backward\r\n':
            print('Shutter closed')
        else:
            print('Shutter motor sent vague answer')
        return

    def calibrationMvmt(self,mvmt):
        """
        Change the origin of the the stepper.
        
        mvmt: a function to adjust the height of the stepper while setting it
        as the new origin.
        type mvmt: Function. (P_up1 or 2, or P_down1 or 2)
        
        return: None.

        """
        mvmt()
        self.pgenCoord = 0
        return

    def P_up2(self): #+0.025
        '''
        Increases the height of the stepper by 1/4 of a marking (+0.025).
        
        Return: None.
        '''
        if self.pgenReady == False:
            msgbox.showerror(title='Error',message='Pgen stepper motor not ready')
            return
        self.Pgen.write(b'2,400=')
        self.pgenCoord += .025
        print("+0.025")
        return
    
    
    def P_up1(self): #+0.001
        '''
        Increases the height by 1/100 of a marking (+0.001).
        
        Return: None.
        '''
        if self.pgenReady == False:
            msgbox.showerror(title='Error',message='Pgen stepper motor not ready')
            return
        self.Pgen.write(b'2,16=')
        self.pgenCoord += .001
        print("+0.001")
        return
    
    
    def P_down2(self): #-0.025
        '''
        Decreases the height of the stepper by 1/4 of a marking (+0.025).
        
        Return: None.
        '''
        if self.pgenReady == False:
            msgbox.showerror(title='Error',message='Pgen stepper motor not ready')
            return
        self.Pgen.write(b'1,400=')
        self.pgenCoord -= .025
        print("-0.025")
        return
    
    
    def P_down1(self): #-0.001
        '''
        Decreases the height of the stepper by 1/4 of a marking (+0.025).
        
        Return: None.
        '''
        if self.pgenReady == False:
            msgbox.showerror(title='Error',message='Pgen stepper motor not ready')
            return
        self.Pgen.write(b'1,16=')
        self.pgenCoord -= .001
        print("-0.001")
        return