# PetriScanner2
Free open source high definition digital plate reader.

# PetriScanner2 – QuickStart

Welcome to the QuickStart guide of PetriScanner.  In this tutorial you are going to learn how to set your experiments, acquire your images, and extract relevant information that characterize each microbial colony.
Petri Scanner is a python module that focuses in facilitating the digital plate reading (DPR) process, aiming for an accurate growth measurement of a high density of microbial colonies, while simultaneously allowing to study the effect of different drugs in their growth.

## Overview:

With the aim of reaching both, those familiar and unfamiliar with programming/scripting, we ought to use Python and ImageJ - both powerful programming languages with "easy to interpret" commands- that will allow users to tune a wide range of parameters, resulting in an improvement on the analysis if their images.
This library is comprised of 3 different sections:
* Image Acquisition
  * [Python](https://www.python.org/)
* Image Analysis
  * [ImageJ - Fiji](https://imagej.nih.gov/ij/)
* Data Analysis
  * Python
		
## Setup

### Download and install

* [Fiji](https://imagej.net/Fiji/Downloads)
  * [MorpholibJ](https://imagej.net/MorphoLibJ#Installation)
 
* [Python >= 3.7.4](https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe)
  * Make sure that this version of python is recognized as your default internal command. If you are not familiar with environmental variables, avoid the use of Anaconda or Miniconda.

* Visual Studio Community (version >= 2014).
  * .NET desktop development
  * Universal Windows Platform development
  * Python development
  
* PetriScanner
  * Add the path of your fiji.app to Path/to/PetriScanner/defaults/pth_to_imageJ.txt
  * Click on Install_PetriScanner.bat to finalize the installation.

For deeper insight check: Installation and Scanner Setup.<br>
*Do not forget to connect the scanner to your computer, and download required drivers for your scanner.*
*For further information about installing the software or hardware please refer to ./Manuals/PetriScanner-1_of_6-Setting_up_the_Scanner.docx*

## Creating plate holders

### If you have access to 3D printer:<br>
Print the files in ./Petriscanner/Fisical_boards/Plate_Holder.stl <br>
 * If you need to edit the file, use Board_plus_Spaces.stl instead.<br>
### If you have access to a lasercutter:<br>
Print the files in ./Petriscanner/Fisical_boards/Plate_Holder.<br>
		*Light colored material is recommended.*
		
## Preparing an experiment

Plate the number of desired CFU in a Petri dish with 25 ml of Solid Agar by diluting the inoculum in a final volume of 500µl of a liquid version of your medium or any other resuspension liquid. Shake gently until the liquid covers the totality of the plate. Let dry for 2-5 minutes, or until there are no visible puddles. Once it's finished, clean the bottom of the dish and place them in the scanner.
<br>*For further information about experiment preparation refer to  ./Manuals/PetriScanner-2_of_6-Agar_Plate_Preparation*

## Scanning your board

The first time you use the software you will need to digitalize your board. Place it on top of the flatbed scanner and make sure it fits tightly, any movements will lead to noisy measurements. Once it is located steadily on the scanner close the lead and open the python GUI, select the parameters that better fit your experimental set-up and click on Scan Board. After a couple of minutes, you will have a digitalized version of the plate holder. You should be able to save it on PetriScanner/boards/.  Once finish this process open ImageJ and go to Plugins > Macros > Detect_board. Select your recently scanned board and you are good to go. <br>

*In the case that your board was incorrectly segmented due to low contrast, etc., you can mark the holes manually with the circle tool on ImageJ.*<br>
*For further information about GUI parameters refer to ./Manuals/PetriScanner-3_of_6-Preparing_1st_exp*<br>

## Monitoring growing cultures

Once you have your colonies ready to grow, place the Petri dish on the corresponding space of the plate holder. After all petri dishes are placed on the board open the python GUI and fill all the necessary fields. When you are finished click on Start Scan. All images will be saved depending on the number of plates that you used. <br>
<br>*For further information about GUI parameters refer to ./Manuals/PetriScanner-4_of_6-Pythons_GUI*

## Data Analysis
Finally, once your scans are completed you click on the Extract_Data.py found on PetriScanner’s  root. Or you can run the following command directly from python: 

import PetriScanner_Analize as ps
import os 

```pth_in = input('Enter the path to the folder containing the experiment to be analized:\n\t')
pth_in = pth_in+'/' if pth_in[-1:] != '/' else pth_in
exist = os.path.exists(pth_in)
while not exist:
    pth_in = input('The path that you entered is incorrect, try again:\n\t')
    pth_in = pth_in+'/' if pth_in[-1:] != '/' else pth_in
    exist = os.path.exists(pth_in)
    
Exp = ps.Experiment(pth_in)
Exp.TimeDependent  (save = pth_in+'TimeDependent.csv')
Exp.TimeIndependent(save = pth_in+'TimeIndependent.csv')
```
This will generate 2 output files reporting several parameters for each colony and time frame. Files are split between time dependent and independent attributes. Area, color and radius and their magnitude of change are examples of time dependent attributes, while appearance time, maximum size and maximum growth rate are examples of time independent ones.  Relationship between tables can be found by the colony Id, which remains constant across tables. 
<br>
*For further information refer to ./Manuals/PetriScanner-5_of_6-Analyzing_images*<br>
*All other problems, please refer to ./Manuals/PetriScanner-7_of_6-Troubleshooting*


