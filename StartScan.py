#!/usr/bin/env python
# coding: utf-8

# # GUI for Capturing images
# ### Importing libraries

# In[2]:


import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
import pandas as pd
import numpy as np
import datetime
import pyinsane2
import getpass
import time
import os


# ### Defining classes

# In[3]:


class quitButton(tk.Button):
    '''
    Exit button
    '''
    def __init__(self, parent):
        tk.Button.__init__(self, parent)
        self['text'] = 'Close'
        # Command to close the window (the destroy method)
        self['command'] = parent.destroy
    
    
class ErrorWindow:
    '''
    Pop-up error window
    '''
    def __init__(self,error_message):
        if not tk._default_root: # check for existing Tk instance
            error_window = tk.Tk()
            error_window.withdraw()
        tk.messagebox.showerror("ERROR",error_message)


# ## Lesser functions

# In[4]:


def showerror(message):
    '''
    Calls messagebox box with error window.
    '''
    tk.messagebox.showerror('XYZ ERROR', message, parent=root)
    
        
def browse_button():
    '''
     Allow user to select a directory and stores its path in a global variable. 
    '''
    global Path_2_Folder
    filename = filedialog.askdirectory()
    Path_2_Folder.set(filename)

def progress(count, Parameters, Max = False):
    '''
    Function that updates and controls the progress bar. 
    '''
    progressbar["value"]=count
    if Max: 
           progressbar["maximum"] = Max
    else:
        progressbar["maximum"]= Parameters['Duration']*60/Parameters['Interval']

    
    
def  _read():
    '''
    Retrieves the values of all variables captured by the GUI.
    '''
    global Parameters
    global content
    Parameters = {}

    Ints    = ['Resolution'   , 'Starting_image', 'Contrast', 'Brightness']
    Bool_L  = ['Perturbations', 'White_Bkgrd'   , 'Red_Colonies']
    Floats  = ['Duration'     , 'Interval']
    Strings = ['Exp_name'     , 'Scanner_name'  , 'Format', 'Board_Name', 'StartTime', 'StartDate']
    Leyend  =  '[Optional]\n\nBrief project description.'

    for s in Strings: 
        Parameters[s] = _Parameters[s].get()
    for i in Ints: 
        Parameters[i] = int(_Parameters[i].get())
    for f in Floats:
        Parameters[f] = float(_Parameters[f].get())
    for l in Bool_L:
        Parameters[l] = [int(i.get()) for i in _Parameters[l]]
        Parameters[l] = str(Parameters[l]).replace(' ','')

        
    Parameters['Conditions'] = [i.get() for i in _Parameters['Conditions']]
    Parameters['Conditions'] = str((Parameters['Conditions'])).replace(' ','')
    
    Parameters['Path'] = _Parameters['Path'].get()+'/'
    content = Text_Description.get(1.0, "end-1c")
    
    if content != Leyend:
        Parameters['Description'] = content.replace('\n','').replace('\t','    ')
    else:
        Parameters['Description'] = '...'
    
def create_circular_mask(h, w, center=None, r=None):
    '''
    Receives a height and a width of a Matrix, then creates an elliptical mask with a radius (r).
    If no center is given, the middle of the image is selected. 
    If no radius is given, it creates a mask that will stretch till H, and W. 
    
    Input:
    ---------------------
    h (int): 
        Height of the mask. 
    w (int):
        Width of mask.
    center: 
        Center of the image.
    r (int): 
       Radius 
    
    Returns:
    ---------------------
        Mask (numpy.Array)
    
    Function retrieved from: 
        https://stackoverflow.com/questions/44865023/circular-masking-an-image-in-python-using-numpy-arrays 
        -alkasm 
        on 14, May 2019

    '''
    if center is None: # use the middle of the image
        center = [int(w/2), int(h/2)]
    if r is None: # use the smallest distance between the center and image walls
        r = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= r
    return mask


def Get_Coords(pth):
    '''
    Reads.board.txt files, and obtains their coordinates.
    '''
    Coordinates = []

    with open(pth, 'r') as file: 
        info = file.read()

    info = info.split('\n')
    Dpi = int(info[1].split(':')[1])
    sf = 800/Dpi

    Coords = [tuple([int(j) for j in i.split('    ')]) for i in info if '    ' in i]
    Coords = pd.DataFrame(Coords, columns=['X', 'Y'])
    
    Coords.sort_values(by=['X', 'Y'], inplace=True)
    X_1 = int(Coords.iloc[[0,1,2]]['X'].mean())
    X_2 = int(Coords.iloc[[3,4,5]]['X'].mean())

    Coords.sort_values(by=['BY'], inplace=True, ascending=True)
    Y_1 = int(Coords.iloc[[0,1]]['Y'].mean())
    Y_2 = int(Coords.iloc[[2,3]]['Y'].mean())
    Y_3 = int(Coords.iloc[[4,5]]['Y'].mean())


    for x in [X_1, X_2]: 
        for y in [Y_3, Y_2, Y_1]: 
            Coordinates.append(tuple([x*sf,y*sf]))
    return(Coordinates)




    
def Cropp_Images(im, Coordinates, Plate_diameter_mm = 87, Exclude_mm = 4.75): 
    '''
    This function receives the image captured by the Board and crops it into 6 different circles. 
    Each circle with a diameter of = Plate_diameter_mm and excluding Exclude_mm from the borders.
    The centers of the images are either taken from a board, or from Coords. 
    
    Input:
    ---------------------
    im (): 
        Image to be cropped.
        
    Plate_diameter_mm (float): 
        Diameter of the petri dish. 
        CellStar petri dishes were measured to be around 87 mm of diameter.
        
    Exclude_mm (float):
        Section of the petri dish that we are going to remove from the analysis. 
        
        
    Coordinates (list): 
        List of 6 tuples.
        
    Returns:
    ---------------------
        List containing 6 images () 
    
    '''
    # This section allows to work with any image size.
        #sf stands for scaling factor
    Cropped_dishes = []
    Dpi = im.size[0]/8.5
    sf  = Dpi/800
    Plate_diameter_mm = int((Plate_diameter_mm*31.6)*sf)
    Exclude_mm       = int((Exclude_mm*31.6)*sf)
   
        
    Coordinates = [(round(i[0]*sf),round(i[1]*sf)) for i in Coordinates]
    
    for x_1, y_1 in Coordinates:
        x_2 = x_1 + Plate_diameter_mm
        y_2 = y_1 + Plate_diameter_mm
        cropped_rectangle = (x_1, y_1, x_2, y_2)
        cropped_im = im.crop(cropped_rectangle)
        mask = create_circular_mask(Plate_diameter_mm, Plate_diameter_mm, r = Plate_diameter_mm/2-Exclude_mm)
        masked_img = np.array(cropped_im)
        masked_img[~mask] = 0    
        masked_img = masked_img[Exclude_mm:-Exclude_mm,Exclude_mm:-Exclude_mm]
        #masked_img = masked_img[(Exclude_mm-10):-(Exclude_mm-10),(Exclude_mm-10):-(Exclude_mm-10)] # We could leave 10 pixels of 0s
        temp = Image.fromarray(masked_img,'RGB')
        Cropped_dishes.append(temp)
    return(Cropped_dishes)


#### Scanner control functions
def Scan(Device, Param):
    '''
    This function makes use of the Pyinsane2 module and captures an image with the scanner. 
    
    Input:
    ---------------------
    Device (pyinsane2.wia.abstract.Scanner): 
        Selected scanner.
    
    Param (Dictionary):
        {'Brightness': Int, 'Contrast': int, 'Resolution': int} 
        
    Returns:
    ---------------------
        Image
        
    **NOTE
        If you want to use this function by itself, you first must start pyinsane by running: 
            pyinsane2.init()
            Device = pyinsane2.get_devices()
    '''
    Device.options['brightness'].value = Param['Brightness']
    Device.options['contrast'].value   = Param['Contrast']
    
    try:
        pyinsane2.set_scanner_opt(Device, 'resolution', [Param['Resolution']])
        pyinsane2.set_scanner_opt(Device, 'mode', ['Color'])
        pyinsane2.maximize_scan_area(Device)
        scan_session = Device.scan(multiple=False)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        Image = scan_session.images[-1]
    finally:
        pyinsane2.exit()
    return(Image)




def Create_Log(Param):
    '''
    Saves the parameters used to scan the images. 
    
    Input:
    ---------------------
        Param(dict):
            Dictionary containing all the experiment parameters.
    Returns:
    ---------------------
        None - Creates an out file at Param['Path'] + Param['Exp_name'] called "Description.txt"
    '''
    with open(Param['Path'] + Param['Exp_name']+ '/Description.txt' , 'w') as File:
        for prop in Parameters:
            File.write(prop+':\t'+str(Parameters[prop])+'\n')
            
            
def MakeFolder(Params):       
    '''
    Creates the folder structure for saving the experiment.
    
    Input:
    ---------------------
        Param(dict):
            Dictionary containing all the experiment parameters.
    Returns:
    ---------------------
        None -  Creates experiment directories.
    '''
    Dir = Parameters['Path'] + Params['Exp_name']
    
    #Create the new folder (if it doesn't exist)
    if not os.path.exists(Dir):
        os.makedirs(Dir)
        os.makedirs(Dir+'/Images/')
    #If it already exist, then create another one with an "-1" added
    elif not os.path.exists(Dir+'-1'): 
        os.makedirs(Dir+'-1')
        os.makedirs(Dir+'-1/Images/')
        Params['Exp_name'] = Params['Exp_name']+'-1'
    #If this one already exists (and we know that this files follow a given format). 
    #We can now elaborate on them and create files with increasing numbers. 
    else:
        new = max([int(i.split('-')[-1]) for i in os.listdir(Parameters['Path']) if Params['Exp_name']+'-' in i])+1
        os.makedirs('{}-{}'.format(Dir,new))
        os.makedirs('{}-{}/Images/'.format(Dir,new))
        Params['Exp_name'] = Params['Exp_name']+'-'+str(new)
    
    Dir = Parameters['Path'] + Params['Exp_name']
    os.makedirs(Dir+'/Raw_csv_results/')
    if 'Interval' in Params:
        for i in range(1,7):
            os.makedirs(Dir+'/Images/'+str(i))
            os.makedirs(Dir+'/Raw_csv_results/'+str(i))
    Create_Log(Params)
    return(Dir+'/')


# ## 3 Main functions of GUI

# In[5]:



def Scanning_Process():
    '''
    Scanning input that makes use of global variables
    
    Input: 
    ---------------------
    None - Makes use of global variables.
    
    Parameters
    
    Returns:
    ---------------------
    Pandas DataFrame
    
    '''
    global count
    _read()


    
    ##This section controls the timed start
    YYYY,MM,DD = [int(i) for i in Parameters['StartDate'].split('/')]
    hh,mm = [int(i) for i in Parameters['StartTime'].split(':')]

    now = datetime.datetime.now()
    Start = now.replace(year = YYYY, month = MM, day = DD, hour=hh, minute=mm, second=0, microsecond=0)
    while datetime.datetime.now() < Start:
        time.sleep(1)
    
    
    
    if List_of_Scanners[0] == 'Error: No detected Scanners':
        ErrorWindow('Error: Failed to detect the scanner.\nMake sure the scanner is properly connected and turned on.')
    else:
        Scanner = Devices[Scanner_dict[Parameters['Scanner_name']]]
        Dir = MakeFolder(Params=Parameters)
        count = 0

        while (Parameters['Duration'] > (count * Parameters['Interval'] / 60)): # 288 it's equal to 48 hours of measurements
            tic = time.clock()
            _Image = Scan(Device= Scanner, Param= Parameters)
            
            Coords = Get_Coords(pth = './boards/{}.board.txt'.format(Parameters['Board_Name'])) ### This was '..boards/{}.board.txt'
            Cropped = Cropp_Images(_Image, Coords)
            
            if count == 0:
                Cord = Cropped[0].size[0]/2
                Centers = [(Cord,Cord)]*6
                with open(Parameters['Path'] + Parameters['Exp_name']+ '/Description.txt' , 'a') as File:
                    File.write("Centers:\t{}".format(str(Centers).replace(' ','')))
                    
            for image in enumerate(Cropped, 1):
                name = Dir+'Images/'+str(image[0])+'/'+str(count+Parameters['Starting_image'])+'.'+Parameters['Format'].lower()
                if (Parameters['Format'] == 'TIFF'):
                    image = image[1].convert('RGB')
                    image.save(name, format='TIFF', compression='tiff_lzw')
                else:    
                    image[1].save(name)
            toc = time.clock()
            count +=1
            try:
                time.sleep(Parameters['Interval']*60-(toc - tic))
                progress(count, Parameters)
                progressbar.update()
            except ValueError:
                continue
        Last = Dir+'LastTimePoint.'+Parameters['Format'].lower()
        if (Parameters['Format'] == 'TIFF'):
            _Image = _Image.convert('RGB')
            _Image.save(Last, format='TIFF', compression='tiff_lzw')
        else:    
            _Image.save(Last)
            

            


def Calibrate():
    '''
    This function aims to help to select the proper lightning conditions for the experiment given a scanner. 
    Captures 64 different images with the combinations:
        8 different brightness values [0,5 ,10 ... 40]
            8 different contrast values [0,5 ,10 ... 40]
    Input:
    ---------------------
        None
        
    Returns:
    ---------------------
        None
        Creates 64 different images saved at Parameters['Path'].
    '''
    global count
    _read()
    
    Parameters['Resolution'] = 300
    Val_2_test = [i for i in range(0,40,5)]

    if List_of_Scanners[0] == 'Error: No detected Scanners':
        ErrorWindow('Error: Failed to detect the scanner.\nMake sure the scanner is properly connected and turned on.')
    else:
        Scanner = Devices[Scanner_dict[Parameters['Scanner_name']]]
        for i in ['Conditions','Interval','Perturbations','Starting_image','White_Bkgrd']:
            Parameters.pop(i)
        Dir = MakeFolder(Params=Parameters)
        count = 0
        
        
        for Brig in Val_2_test:
            for Cont in Val_2_test:
                
                Parameters['Brightness'] = Brig
                Parameters['Contrast']   = Cont

                _Image = Scan(Device= Scanner, Param= Parameters)
                
                Name = '{}Images/Brightness-{}  Contrast-{}.{}'.format(Dir, Parameters['Brightness'],Parameters['Contrast'],Parameters['Format'].lower())
                if (Parameters['Format'] == 'TIFF'):
                    _Image = _Image.convert('RGB')
                    _Image.save(Name, format='TIFF', compression='tiff_lzw')
                else:    
                    _Image.save(Name)

                count +=1
                progress(count, Parameters, Max = len(Val_2_test)**2)
                progressbar.update()

def CreateBoard():
    _read()
    Scanner = Devices[Scanner_dict[Parameters['Scanner_name']]]
    _Image = Scan(Device= Scanner, Param = Parameters)
    _Image = _Image.convert('RGB')
    _Image.save('..boards/{}.tiff'.format(Parameters['Exp_name']), format='TIFF', compression='tiff_lzw')


# ## Scanner and board detection

# In[7]:


## Detecting Boards

Availible_boards = [i.split(".")[0] for i in  os.listdir('./boards/') if '.board' in i]
if len(Availible_boards)== 0: 
    Availible_boards = ['There are no boards available']

## Detecting scanners
pyinsane2.init()
Devices = pyinsane2.get_devices()
if len(Devices) > 1:
    Scanner_dict = {dev[1].nice_name+' -- '+dev[1].options['dev_id'].value.split('\\')[1]:dev[0] for dev in enumerate(Devices)}
elif len(Devices) == 0:
    Scanner_dict = {'Error: No detected Scanners':0}
else: 
    Scanner_dict = {Devices[0].nice_name+' -- '+Devices[0].options['dev_id'].value.split('\\')[1]:0}
List_of_Scanners = list(Scanner_dict.keys())


# ## GUI

# In[ ]:


_Parameters = {'Perturbations':[True]*6,
               'Conditions'   :['temp']*6,
               'White_Bkgrd'  :[True]*6,
               'Red_Colonies' :[True]*6}

count = 0 
Master_Window = tk.Tk()
Master_Window.resizable(width=True, height=True)

Master_Window.title("PetriScanner")
mainframe = ttk.Frame(Master_Window, padding="50 50 50 50")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

###################################################################################
##########################          Dish Layout          ##########################
###################################################################################

Dish_layout = tk.LabelFrame(Master_Window, text="1. Dish Layout: ")#, padx=5, pady=5)
Dish_layout.grid(row=0, column= 0, sticky='W', padx=10, ipadx=10, pady=5, ipady= 12)

ttk.Label(Dish_layout, text="Drug"     ).grid(column=0, row=0, padx=10,  sticky=tk.W, ipady=5, ipadx=2)
ttk.Label(Dish_layout, text="W_Bg"     ).grid(column=1, row=0, padx=0,   sticky=tk.W, ipady=5, ipadx=2)
ttk.Label(Dish_layout, text="TTC"      ).grid(column=2, row=0, padx=10,  sticky=tk.W, ipady=5, ipadx=0)
ttk.Label(Dish_layout, text="Condition").grid(column=3, row=0, padx=10,  sticky=tk.W, ipady=5, ipadx=0)
ttk.Label(Dish_layout, text="Drug"     ).grid(column=4, row=0, padx=0,   sticky=tk.W, ipady=5, ipadx=2)
ttk.Label(Dish_layout, text="W_Bg"     ).grid(column=5, row=0, padx=0,   sticky=tk.W, ipady=5, ipadx=5)
ttk.Label(Dish_layout, text="TTC"      ).grid(column=6, row=0, padx=10,  sticky=tk.W, ipady=5, ipadx=0)
ttk.Label(Dish_layout, text="Condition").grid(column=7, row=0, padx=10,  sticky=tk.W, ipady=5, ipadx=0)

Toogle_Antibiotics = {}
Entry_Conditions   = {}
Toogle_WBkgrd  = {}

for x in range(2):
    for y in range(3):
        _Parameters['Perturbations'][y+3*x] = tk.BooleanVar()
        _Parameters['Perturbations'][y+3*x].set(False) #set check state
        Toogle_Antibiotics[y+3*x] = tk.Checkbutton(Dish_layout, var= _Parameters['Perturbations'][y+3*x])
        Toogle_Antibiotics[y+3*x].grid(column=x*4, row=y+1, pady=2)

        _Parameters['White_Bkgrd'][y+3*x] = tk.BooleanVar()
        _Parameters['White_Bkgrd'][y+3*x].set(False) #set check state
        Toogle_Antibiotics[y+3*x] = tk.Checkbutton(Dish_layout, var= _Parameters['White_Bkgrd'][y+3*x])
        Toogle_Antibiotics[y+3*x].grid(column=x*4+1, row=y+1, pady=2)

        _Parameters['Red_Colonies'][y+3*x] = tk.BooleanVar()
        _Parameters['Red_Colonies'][y+3*x].set(False) #set check state
        Toogle_Antibiotics[y+3*x] = tk.Checkbutton(Dish_layout, var= _Parameters['Red_Colonies'][y+3*x])
        Toogle_Antibiotics[y+3*x].grid(column=x*4+2, row=y+1, pady=2)
        
        _Parameters['Conditions'][y+3*x] = tk.StringVar()
        Entry_Conditions[y+3*x] = ttk.Entry(Dish_layout, width=10, textvariable=_Parameters['Conditions'][y+3*x])
        Entry_Conditions[y+3*x].grid(column=x*4+3, row=y+1, padx=10, ipadx=0, sticky=(tk.W, tk.E), pady=2)
        Entry_Conditions[y+3*x].insert(0,'Dish_{}'.format(y+3*x+1))
        ttk.Label(mainframe, text="_Parameters['Conditions'][y+3*x]").grid(column=3, row=1, sticky=tk.W)



###################################################################################
##########################      Parameter Layout       ############################
###################################################################################

Param_Layout = tk.LabelFrame(Master_Window, text="2. Parameters: ")
Param_Layout.grid(row=0, column=1, sticky='W', padx=10, ipadx=10, pady=5, ipady=5)

#### First row
_Parameters['Contrast'] = tk.StringVar()
Entry_Contrast = ttk.Entry(Param_Layout, width=10, textvariable=_Parameters['Contrast'], justify= 'center')
Entry_Contrast.grid(column=2, row=1, padx=5, ipadx=5)
Entry_Contrast.insert(0,'25')
ttk.Label(Param_Layout, text="Contrast:  ").grid(column=1, row=1, sticky=(tk.W, tk.E), padx=10, ipadx=5)

_Parameters['Brightness'] = tk.StringVar()
Entry_Brightness = ttk.Entry(Param_Layout, width=10, textvariable=_Parameters['Brightness'], justify= 'center')
Entry_Brightness.grid(column=4, row=1, sticky=(tk.W, tk.E), padx=5, ipadx=5)
Entry_Brightness.insert(0,'15')
ttk.Label(Param_Layout, text="Brightness:").grid(column=3, row=1, sticky=(tk.W, tk.E), padx=5, ipadx=5)


#### Second row

#Resolution_Choices = ['150','300','400','600','800','1200','2400']
with open('./defaults/Possible_Resolutions.txt', 'r') as F: 
    Resolution_Choices = eval(F.read().strip().split('=')[1])

_Parameters['Resolution'] = tk.StringVar(Param_Layout)
OptionMenu_Resolution =tk.OptionMenu(Param_Layout, _Parameters['Resolution'], *Resolution_Choices)
OptionMenu_Resolution.grid(column=2, row=2, sticky=(tk.W, tk.E))
ttk.Label(Param_Layout, text="Resolution:").grid(column=1, row=2, sticky=(tk.W, tk.E), padx=10, ipady=10)
_Parameters['Resolution'].set('800')


OptionMenu_Resolution.grid(column=2, row=2, sticky=(tk.W, tk.E))



_Parameters['Interval'] = tk.StringVar()
Entry_Interval = ttk.Entry(Param_Layout, width=10, textvariable=_Parameters['Interval'], justify= 'center')
Entry_Interval.grid(column=4, row=2, sticky=(tk.W, tk.E), padx=5, ipadx=5, pady=0, ipady=0)
Entry_Interval.insert(0,'10')
ttk.Label(Param_Layout, text="Interval (Min):").grid(column=3, row=2, sticky=(tk.W, tk.E), padx=5, ipadx=5)


#### Third row
_Parameters['Duration'] = tk.StringVar()
Entry_Duration = ttk.Entry(Param_Layout, width=10, textvariable=_Parameters['Duration'], justify= 'center')
Entry_Duration.grid(column=4, row=3, sticky=(tk.W, tk.E), padx=5, ipadx=5, pady=0, ipady=0)
ttk.Label(Param_Layout, text="Duration (Hrs):").grid(column=3, row=3, sticky=(tk.W, tk.E), padx=5, ipadx=5)
Entry_Duration.insert(0,'42')


#### Fourth row
ttk.Label(Param_Layout, text="Scanner:").grid(column=1, row=5, sticky=(tk.W, tk.E),padx=10, ipadx=5)
_Parameters['Scanner_name'] = tk.StringVar(Param_Layout)
_Parameters['Scanner_name'].set(List_of_Scanners[0])
OptionMenu_Scanners =tk.OptionMenu(Param_Layout, _Parameters['Scanner_name'], *List_of_Scanners) 
OptionMenu_Scanners.grid(column=1, columnspan=2, row=6, sticky=(tk.W, tk.E), padx=10, ipadx=5, pady=0, ipady=0)
if List_of_Scanners[0] == 'Error: No detected Scanners':
    OptionMenu_Scanners.configure(fg="red")

ttk.Label(Param_Layout, text="Board:").grid(column=3, row=5, sticky=(tk.W, tk.E), padx=5, ipadx=5)
_Parameters['Board_Name'] = tk.StringVar(Param_Layout)
_Parameters['Board_Name'].set(Availible_boards[0])
OptionMenu_Scanners =tk.OptionMenu(Param_Layout, _Parameters['Board_Name'], *Availible_boards) 
OptionMenu_Scanners.grid(column=3, columnspan=2, row=6, sticky=(tk.W, tk.E), padx=5, ipadx=5, pady=5, ipady=0)
if Availible_boards[0] == 'There are no boards available':
    OptionMenu_Scanners.configure(fg="red")



###################################################################################
#########################     Description Layout       ############################
###################################################################################

Description_Layout = tk.LabelFrame(Master_Window, text="3. Description: ")
Description_Layout.grid(row=0, column= 2, columnspan=2, sticky='W', padx=10, ipadx=10, pady=10, ipady=5) 

Leyend = '[Optional]\n\nBrief project description.'

Scroll_Bar = tk.Scrollbar(Description_Layout)
Scroll_Bar.grid(row=0, column= 3, padx=0, ipadx=0, pady=8, ipady=0)
Text_Description = tk.Text(Description_Layout, width=30, height=7)
Text_Description.grid(row=0, column= 2, columnspan=2, padx=15, ipadx=0, pady=8, ipady=0)
Scroll_Bar.config(command=Text_Description.yview)
Text_Description.config(yscrollcommand=Scroll_Bar.set)
Text_Description.insert(tk.END, Leyend)



###################################################################################
########################     Output files Layout       ############################
###################################################################################

Output_Layout = tk.LabelFrame(Master_Window, text="4. Output: ")
Output_Layout.grid(row=2, column= 0,  columnspan=2, sticky='W', padx=10, ipadx=10, pady=5, ipady=5)


Path_2_Folder = tk.StringVar()
Label_Dir = ttk.Label(Output_Layout, textvariable=Path_2_Folder)
Label_Dir.grid(column=1, row=2, padx=5, ipadx=5, pady=2, ipady=0)
Label_Dir.configure(background="white")
Path_2_Folder.set('/Users/'+getpass.getuser()+'/Pictures')


Button_Browse = tk.Button(Output_Layout, text="Browse folder ...  ", command=browse_button)
Button_Browse.grid(column=1, row=1, padx=5, ipadx=5, pady=2, ipady=0)
_Parameters['Path'] = Path_2_Folder


ttk.Label(Output_Layout, text="Experiment name:").grid(column=2, row=1, columnspan=1, sticky=(tk.W, tk.E), padx=20, ipadx=0)
_Parameters['Exp_name'] = tk.StringVar()
Entry_Exp_name = ttk.Entry(Output_Layout, width=25, textvariable=_Parameters['Exp_name'], justify= 'center')
Entry_Exp_name.grid(column=2, row=2, columnspan=1, sticky=(tk.W, tk.E), padx=20, ipadx=0)
Entry_Exp_name.insert(0,'Experiment_000')


ttk.Label(Output_Layout, text="Starting image:").grid(column=5, row=1, columnspan=1, sticky=(tk.W, tk.E), padx=20, ipadx=0)
_Parameters['Starting_image'] = tk.StringVar()
_Parameters['Starting_image'] = tk.Spinbox(Output_Layout, from_= 1, to = 2**16, width = 5)
_Parameters['Starting_image'].grid(column=5, row=2, sticky=(tk.W, tk.E), padx=20, ipadx=0)


ttk.Label(Output_Layout, text="Format:").grid(column=6, row=1, columnspan=1, sticky=(tk.W, tk.E), padx=20, ipadx=0)
Format_Choices = ['BMP', 'JPEG', 'PNG', 'TIFF']
_Parameters['Format'] = tk.StringVar(Output_Layout)
OptionMenu_Format =tk.OptionMenu(Output_Layout, _Parameters['Format'], *Format_Choices) 
OptionMenu_Format.grid(column=6, row=2, sticky=(tk.W, tk.E))
_Parameters['Format'].set('PNG')


ttk.Label(Output_Layout, text="Start Date:\nyyyy/mm/dd").grid(column=7, row=1, columnspan=1, sticky=(tk.W, tk.E), padx=10, ipadx=0)
_Parameters['StartDate'] = tk.StringVar()
Entry_Exp_name = ttk.Entry(Output_Layout, width=14, textvariable=_Parameters['StartDate'], justify= 'center')
Entry_Exp_name.grid(column=7, row=2, columnspan=1, sticky=(tk.W, tk.E), padx=10, ipadx=0)
Entry_Exp_name.insert(0,time.strftime("%Y/%m/%d", time.gmtime()))


ttk.Label(Output_Layout, text="Start Time:\n   hh:mm").grid(column=8, row=1, columnspan=1, sticky=(tk.W, tk.E), padx=10, ipadx=0)
_Parameters['StartTime'] = tk.StringVar()
Entry_Exp_name = ttk.Entry(Output_Layout, width=10, textvariable=_Parameters['StartTime'], justify= 'center')
Entry_Exp_name.grid(column=8, row=2, columnspan=1, sticky=(tk.W, tk.E), padx=10, ipadx=0)
_now = datetime.datetime.now()
Entry_Exp_name.insert(0,'{}:{}'.format(_now.hour,_now.minute))




###################################################################################
#########################         Progress Bar          ###########################
###################################################################################

Progress_Layout = tk.LabelFrame(Master_Window, text="Progress: ")
Progress_Layout.grid(row=2, column= 2,  columnspan=2, sticky='W', padx=10, ipadx=10, pady=5, ipady=5)

maxValue=  (eval(Entry_Duration.get())*60/eval(Entry_Interval.get()))

progressbar=ttk.Progressbar(Progress_Layout, orient="horizontal", length=250, mode="determinate")
progressbar.grid(column=5, row=2, sticky=(tk.W, tk.E), padx=20, ipadx=0, pady=5)

progressbar["value"]  = count
progressbar["maximum"]= maxValue



###################################################################################
#########################     Buttons Lower section     ###########################
###################################################################################



Check = tk.Button(Master_Window, text="Calibrate", command= Calibrate)
Check.grid(column=0, row=4, sticky=(tk.W, tk.E), padx=15, pady=15, ipadx = 0)

Print = tk.Button(Master_Window, text="Scan Board", command= CreateBoard)
Print.grid(column=1, row=4, sticky=(tk.W, tk.E), padx=15, pady=15, ipadx = 15)


QuitButton = quitButton(Master_Window)
QuitButton.grid(column=2, row=4, sticky=(tk.W, tk.E), padx=0, pady=15, ipadx = 0)

Print = tk.Button(Master_Window, text="Start scan", command= Scanning_Process)
Print.grid(column=3, row=4, sticky=(tk.W, tk.E), padx=15, pady=15, ipadx = 0)



Master_Window.mainloop()


# In[ ]:




