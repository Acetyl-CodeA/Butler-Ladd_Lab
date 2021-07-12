# Butler-Ladd_Lab

This project has been developed to control an experimental build using Python. To learn more about the experiment, see:
https://www.che.ufl.edu/electro-hydrodynamic-migration-drives-the-concentration-of-dna/

The primary aspects of the build are:
1) Control a microscope using a developer SDK
2) Control an electric field generator using PyVISA
3) Control two Arduinos to control a shutter motor and a stepper motor
4) Put everything together in a simple GUI constructed in Tkinter
5) Run easily reproduceable experiments using experimental presets developed in the GUI's built-in text editor

The two branches of this build are main and EXE-Only-Version:

The main branch controls the microscope using a C++ wrapper library for the SDK which is accessed from Python using CTypes. 
  It takes in the raw camera data from the wrapper library, writes it to a .txt file to store it, and can process it later using the executable stored in Image_Processor_Argv.
  It has successfully run simplified experiments, so it is the main build.
  
The side branch EXE-Only-Version controls the microscope using a simpler approach where all of the picture taking and processing is done using a simple executable.
  No CTypes is necessary for this branch because the image processing is done in the executable. Currently there are issues with the image processing aspect, so this
  branch remains a work-in-progress side branch. If this executable can be refined, it will reduce delay in taking pictures significantly.
