#!/usr/bin/env python
# coding: utf-8

#  
#  # Main library
#  
#  ## Setup functions:
#  
#  **CreateRunner -** Creates a .bat file that you can drag to the command line and execute in a headless manner in a server ithout a GUI.
#  
#  **Pth_2_ImageJ -** Retrieves the location of the ImageJ path file.
#  
#  
#  **setupMacros -** Adds our software to the startup macros.

# In[2]:


#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
# 
#  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.



# Already included in python
import os
import random as rn
import copy

# Installation needed
import numpy as np
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
from scipy.signal import savgol_filter as Savgol
import time
import seaborn as sns
from matplotlib import pyplot as plt



def CreateRunner(path , CreateFiles = True, T_Type = 'Otsu', Selected_dishes = [1,2,3,4,5,6], watershed = True , 
                 Rmv_Bkgrnd = True , verbose = True, Color_correction = True, 
                 detect_t = 270, Avg_col_size = 1.68):
    '''
    Creates a .bat file that you can drag to the command line and execute in a headless manner in a server without a GUI.
    
    path
        str 
        Path to the experiment folder. 
    
    CreateFiles
        bool - True
        If True, it generates a file that you can drag to the command line, by creating a macro capable of receiving 
        the 
        
    T_Type
        str -   "Otsu"
        Any of the options on the following list:  
        ["Otsu","Huang","Intermodes","IsoData","Li","MaxEntropy","Mean", "MinError",
        "Minimum","Moments","Percentile","RenyiEntropy","Shanbhag","Triangle","Yen" ]
    
    watershed
        bool - True
        Whether or not watershed is to be performed.
        
    Selected_dishes 
        List - [1,2,3,4,5,6]
        Dishes selected from experiment file.
        
    watershed 
        bool - True
        Whether to perform watershed algorithm or not.
        
    signal
        bool - True
        Either to perform background correction or not.

    verbose
        bool - True
        If input should be printed out or not. 

    Color_correction
        bool - True
        If color correction should be performed or not.

    detect_t
        int - 270 
        Time when colonies start being detected, 270 minutes - 4.5 hours

    Avg_col_size
        float - 1.68 
        Watershed variation (grayscale or binary) is performed based on size. If colonies are bigger than Avg_col_size
        a different type of threshold is used. 
    '''
    path = path if path[-1]=='/' else path+'/'
    watershed = '1' if watershed else '0'
    Rmv_Bkgrnd = '1' if Rmv_Bkgrnd else '0'
    verbose = '1' if verbose else '0'
    Color_correction = '1' if Color_correction else '0'
    Selec_d = ''
    for d in range(1,7):
        if d in Selected_dishes:
            Selec_d += '1_'
        else:
            Selec_d += '0_'
    Selected_dishes = Selec_d[:-1]
    
    #This are the variables that will become the command line arguments.
    Input = 'path {} --T_Type {} --Selected_dishes {}  --watershed {} --Rmv_Bkgrnd {} --verbose {} --Color_correction {} --detect_t {} --Avg_col_size {}'.format(
            path , T_Type , Selected_dishes ,  watershed, Rmv_Bkgrnd, verbose , Color_correction , detect_t ,  Avg_col_size)

    #Pth_2_exe - Path to FIJIs executable
    Pth_2_exe = Pth_2_ImageJ()+[i for i in os.listdir(Pth_2_ImageJ()) if 'exe' in i][0]
    #We create Headless_runner, which is a .ijm file that contains the instructions to run the Ps-Headless macro.
    Pth_2_Runner = Pth_2_ImageJ()+'macros/PetriScanner-Headless_runner.ijm'
    
    #This is what the runner command is, as you can see, it will be something like: 
    # Imj.exe  --Run in headless manner the runner. The runner has all of the inputted values.
    Headless = '{} --ij2 --console --headless --run {}'.format(Pth_2_exe, Pth_2_Runner)
    
    if CreateFiles:
        with open(Pth_2_Runner, 'w+') as Macro: 
            Macro.write('runMacro("PetriScanner-Headless.ijm","{}")'.format(Input)) 

        with open('./Start_headless.bat', 'w+') as Runner: 
            Runner.write(Headless)
        
    return(Headless)
    
    
    
def Pth_2_ImageJ():
    '''
    Retrieves the location of the ImageJ path file.
    '''
    with open('defaults/pth_to_imageJ.txt') as pth:
        Path = pth.read().strip()
        Path = Path.replace('\\','/')
        Path = Path if Path[-1] == '/' else Path + '/'
    return(Path)

def setupMacros(pth = False):
    '''
    Adds PetriScanner code to the startup macros.\n\tpth = Path to StartupMacros file inside of ../fiji-win64/Fiji.app/macros/\
StartupMacros
    '''
    import getpass, os
    
    if (not pth): 
        pth = Pth_2_ImageJ()+'macros/'
        pth = pth+[f for f in os.listdir(pth) if 'StartupMacros' in f][0]

    with open('./macros/PetriScanner_AllMacros.ijm','r') as f:
        to_append = f.read()
        
    flag = 'PetriScanner_instalation = true;'
    
    with open(pth,'r+') as f: 
        StartUp = f.read()
        if flag not in StartUp:
            f.write(to_append)
            f.write(flag+'\n')
            print(pth)
            print('Installation completed!')
        else:
            print('PetriScanner already installed.')
            
    for F in ['PetriScanner-Headless.ijm']:

        with open('./macros/{}'.format(F),'r') as f:
            New_file = f.read()

        with open(os.path.dirname(pth)+'/{}'.format(F), 'w') as new:
            new.write(New_file)


# ## Data processing functions:
# 
# **reverse_read_csv** Shifts the index of a csv file.
# 
# **ReadRawResults**   Reads the output of ImageJ PetriScanner plugin and merges the different results of the analized particles csvs into a pandas DataFrame.
#  
#  
# **ReadDescription** Reads Description.txt file and turns it into a python dictionary.
# 
# **Change** Recieves a list, returns a list with the difference between List[pos_i]-List[pos_i-1] + a 0 added to the end.
# 
# **ExtremaPos** Recieves a list, then returns the index position of the [first|last] [maximum | minimum] value withing the list.
# 
# **Color_Intensity** Assigns an intensity to each color channel with the use of Euclidian distance.
# 
# **Remove_Duplicates** If two different colonies share an Id in the same time point, removes all smaller ones and keeps the bigger one. 
# 

# In[ ]:


def reverse_read_csv(Path, **kwargs):
    '''
    Shifts the index of a csv file.
    '''
    tmp = pd.read_csv(Path, **kwargs)
    tmp.index = range(tmp.shape[0], 0, -1)
    return(tmp.sort_index())

# Function No. 1 - Read csv files (uses function 5)
def ReadRawResults(pth, dish, No_Slices = 0,  Add_to_Id = 0, reverse = True, Filter_Dupl = True): 
    '''
    Reads the output of ImageJ PetriScanner plugin and merges the different results of the analyzed particles csvs into a pandas DataFrame.
    
    Input:
    ---------------------
    pth (str): 
        Path of the directory containing the results of the image analysis software. 
        Namely: Particle_information.csv, Particle_information_[blue|green|red|id].csv

    Dish (list):
        Selects the dishes to be read from python
    
    reverse (bool):
        Reads csv and reorders it, so the first row is now the last and so on. 
        
    Returns:
    ---------------------
    Pandas DataFrame
    
    Sample: 
    ---------------------
    ReadRawResults(pth = C:Path/to/Experiment/location/)
    '''
    formats   = ['BMP', 'JPEG', 'PNG', 'TIFF', 'TIF']
    N_images  = 0 #Number of images that were captured. Has to be > 0.

    To_Drop = ['BX', 'BY', 'Width', 'Height', 'IntDen','RawIntDen', 'Mean']
    All_Df = []
    target = 'Raw_csv_results/{}/Particle_information.csv'.format(dish)
    _pth = pth+target if pth[-1] == '/' else pth+'/' + target
        
    if (reverse):
        Df = reverse_read_csv(_pth, index_col=' ')
        Ids = reverse_read_csv(_pth[:-4]+'_IDs.csv', usecols=['Mode'])
    else: 
        Df = pd.read_csv(_pth, index_col=' ')
        Ids = pd.read_csv(_pth[:-4]+'_IDs.csv', usecols=['Mode'])
            
    Df['Id'] = [int(c) for c in Ids.Mode]
    for color in ['red','green','blue']:
        Pth = reverse_read_csv(_pth[:-4]+'_{}.csv'.format(color), index_col=' ')
            
        Df['Color_'+color[0].upper()] = [round(c,2) for c in Pth['Mean']]
        Df['StdDev_'+color[0].upper()] = [round(c,2) for c in Pth['StdDev']]

    for prop in To_Drop:
        Df.pop(prop)
    Df['X'] = Df.pop('XM')
    Df['Y'] = Df.pop('YM')
    Df['Id']= Df['Id'] + Add_to_Id
    Df['DishNo']= dish
    Add_to_Id = max(Df['Id'])
    All_Df.append(Df)
    del(Df)
        
    All_Df = pd.concat(All_Df)
    All_Df = All_Df.dropna(axis=0, how='any')
    All_Df.index = range(All_Df.shape[0])
    
    if reverse:
        #Parameter is received internally.
        if No_Slices > 0: 
            N_images = No_Slices

        #Number of images is obtained by counting number of images in Exp/Images/dish
        if N_images == 0:
            if 'Images' in os.listdir(pth):
                if  os.path.isdir(pth+'/Images/'+str(dish)+'/'):
                    Images = os.listdir(pth+'/Images/'+str(dish))
                    N_images = 0
                    for im in Images:
                        if im.split('.')[1].upper() in formats: 
                            N_images += 1

        #Number of images is obtained by scanning log file. If version < 2, probably this option is not available in old files.
        if N_images == 0:
            if N_images == 0 or 'Images' not in os.listdir(pth):
                pht_2_log = pth+'/Raw_csv_results/'+str(dish)+'/log.txt'
                if os.path.isfile(pht_2_log): 
                    with open(pht_2_log, 'r') as log: 
                        for line in log:
                            if 'dataset' in line.lower(): 
                                N_images = int(re.findall(r'\d+', line.split(':')[1])[0])

        #Worst case scenario, we ask the user for the number of images in file. 
        if N_images == 0:
            if N_images == 0:
                N_images = int(input('Number of images on the experiment was not found.\nAdd number of images (int):\t'))
        All_Df['Slice'] = (N_images+1)-All_Df.Slice
        
    if Filter_Dupl:
        All_Df = Remove_Duplicates(All_Df)
    return(All_Df)


# Function No. 2 - Read description file
def ReadDescription(pth):
    '''
    Reads Description.txt file and turns it into a python dictionary.
    
    Input:
    ---------------------
    pth (str): 
        Path to Description.txt file, generated by the scanning process of the experiment.
        
    Returns:
    ---------------------
    Dictionary (dict)
    Contains the parameters of the experiment: 
    
        Sample_Return = {'Conditions:':   ['Ctrl_1', 'Amp_1', 'Kan_1', 'Ctrl_2', 'Amp_2', 'Kan_2'], #List
                         'Perturbation:': [False, True, True, False, True, True],

                         'Brightness:': 15, #Int
                         'Contrast:': 25,
                         'Resolution:': 300,
                         'Starting_image:': 1,

                         'Exp_name:': 'Test', #Str
                         'Description:': 'This is a test description.',
                         'Path:': 'Path/to/somewhere/',
                         'Scanner_name:': 'WIA CanoScan LiDE 210 -- 0000',
                         'Format:': 'TIFF',

                         'Duration:': 45, #Floats
                         'Interval:': 0.5} 
                         
    Sample: 
    ---------------------
    ReadDescription(pth = C:Path/to/Experiment/location/Description.txt)
    '''
    with open(pth) as file: 
        Text = file.read()

    _dict = {}
    for section in Text.split('\n'):
        if section!= '':
            key,value = section.split('\t')
            key = key[:-1]
            try:
                _dict[key] = eval(value)
            except NameError:
                _dict[key] = value
            except SyntaxError:
                _dict[key] = value
        
    return(_dict)

# Function No. 3 - Measure change from a list.
def Change(List):
    '''
    Receives a list, returns a list with the difference between List[pos_i]-List[pos_i-1] + a 0 added to the end.

    Input:
    ---------------------
    List (list):
    
    Returns:
    ---------------------
    list
    '''
    return([List[pos_i]-List[pos_i-1] for pos_i in range(1,len(List))]+[0.0])


# Function No. 4 - Retrieve position of maximum or minimum.
def ExtremaPos (List, extrema = 'max', retrieve = 'first', _tuple = False):
    '''
    Receives a list, then returns the index position of the [first|last] [maximum | minimum] value withing the list.
    
    Input:
    ---------------------
    List (list):
        
    extrema (str): 
        max || min

    retrieve (str): 
        first || last
        
    _tuple (bool): 
        if true, returns (extrema,pos)
        
    Returns:
    ---------------------
    index (int) 
        0 based position of either the maximum or the minimum. 
    '''
    if extrema == 'max':
        if retrieve == 'first':
            if _tuple:
                return(max(List),List.index(max(List)))
            else:
                return(List.index(max(List)))
        elif retrieve == 'last':
            if _tuple:
                return(max(List),len(List)-1-List[::-1].index(max(List)))
            else:
                return(len(List)-1-List[::-1].index(max(List)))
    elif extrema == 'min':
        if retrieve == 'first':
            if _tuple:
                return(min(List),List.index(min(List)))
            else:
                return(List.index(min(List)))
        elif retrieve == 'last':
            if _tuple:
                return(min(List),len(List)-1-List[::-1].index(min(List)))
            else:
                return(len(List)-1-List[::-1].index(min(List)))
            
# Function No. 6 - Assigns an intensity given a color.
def Color_Intensity(RGB, color = 'R'):
    '''
     Assigns an intensity to each color channel with the use of Euclidian distance.
     
     
    This function evaluates how intense is either the red, blue or green color of a pixel with an Euclidian distance approach.
    
    Parameters
    ----------
    RGB (tuple of size 3):
        RGB representation of the color.

    color (str):
        Valid options: 
        
            ["R" | "G" | "B"]
            R - Red
            G - Green 
            B - Blue

            *** Only the first letter of the color parameter is evaluated.
    Returns: 
    ----------
        float ranging from 0 to 1.
    '''
    if color[0].upper() not in ['R', 'G', 'B']:
        return("\"{}\" is not a valid option".format(color))
    elif color[0].upper() == 'G':
        RGB = RGB[1],RGB[2],RGB[0]
    elif color[0].upper() == 'B':
        RGB = RGB[2],RGB[0],RGB[1]

    Int = np.sqrt((255-RGB[0])**2+(0-RGB[1])**2+(0-RGB[2])**2)/255
    Int = (1.7320508075688774 - Int)/1.7320508075688774
    return(Int)

# Function No. 8 - Remove_Duplicates

def Remove_Duplicates(Data):
    # First iteration
    Temp = {}
    Biggest_cols = []
    To_remove    = []

    #For every row in Data: 
    for row,Values in Data.iterrows():
        Id = '{}_{}'.format(int(Values['Slice']),int(Values['Id']))

        if Id not in Temp:
            Temp[Id] = [[row, int(Values['Area'])]]
        else: 
            Temp[Id].append([row, int(Values['Area'])])


    for row in Temp: 
        if len(Temp[row])>1:
            info = np.array(Temp[row])
            True_Col = info[:,0][ExtremaPos(list(info[:,1]))]
            #Biggest_cols.append(True_Col)
            To_remove += [i for i in info[:,0] if i != True_Col]

    Data.drop(To_remove, inplace=True)
    Data.index = range(Data.shape[0])
    return(Data)


# 
#  ## Image acquisition functions
#  
#  **getorigin**    This function allows the user to select the antibiotic source in the image. Then it changes the new source in the description file.

# In[ ]:


# Function No. 7 - Get centers.
def LastPicture(Pth):
    Images = os.listdir(Pth)
    Max = max([int(im[2:-4]) for im in Images])
    Last_im = [im for im in Images if str(Max) in im]
    return('{}/{}'.format(Pth,Last_im[0]))


class quitButton(tk.Button):
    '''
    Exit button
    '''
    def __init__(self, parent):
        tk.Button.__init__(self, parent)
        self['text'] = 'Close'
        # Command to close the window (the destroy method)
        self['command'] = parent.destroy
        
        
def GetCenter(Exp_Pth, Dish, Path_2_image = False):
    # Formatting input
    Exp_Pth = Exp_Pth if Exp_Pth[-1] == '/' else Exp_Pth+'/'

    
    with open(Exp_Pth+'Description.txt') as File: 
        Txt = File.read()

    Description,Centers = Txt.split('Centers:\t')
    Description+='Centers:\t'

    Centers = eval(Centers)
    Coords  = Centers[Dish-1]


    _width  = 800
    _height = 800

    # Determine the origin by clicking
    def getorigin(eventorigin, color = "#00ffff"):
        '''
        This function allows the user to select the antibiotic source in the image. Then it changes the new source in the description file.
        '''
        global Temp_y, Temp_x
        Temp_x = eventorigin.x
        Temp_y = eventorigin.y

        #Drawing cross hair.
        x1, x2 = (eventorigin.x, eventorigin.x)
        y1, y2 = (eventorigin.y - 10 , eventorigin.y + 10)
        V_line = Main_Window.create_line(x1, y1, x2, y2, fill=color, width=2)
        x1, x2 = (eventorigin.x - 10, eventorigin.x + 10)
        y1, y2 = (eventorigin.y, eventorigin.y)
        H_line = Main_Window.create_line(x1, y1, x2, y2, fill=color, width=2)


        if H_line > 3:
            Main_Window.delete(H_line-2)
            Main_Window.delete(V_line-2)
        #print(tuple([round((i/_height)*Size[0]) for i in [Temp_x, Temp_y]]))

    def Save():
        Centers[Dish-1] = tuple([round((i/_height)*Size[0]) for i in [Temp_x, Temp_y]])
        with open('{}Description.txt'.format(Exp_Pth), 'w') as output:
            output.write(Description+str(Centers).replace(' ',''))
            
    Master_Window = tk.Tk()

    global Temp_y, Temp_x
    Temp_y, Temp_x = None, None

    #setting up a tkinter canvas
    Main_Window = tk.Canvas(Master_Window, width= _width , height= _height)
    Master_Window.title("PetriScanner - Selecting Centers Dish {}".format(Dish))
    Main_Window.pack()


    #Opening image file to select the center.
    #File = askopenfilename(parent=Master_Window, initialdir="./",title='Select an image')
    File = LastPicture('{}Images/{}'.format(Exp_Pth, Dish))
    original = Image.open(File)
    Size = original.size
    original = original.resize((_width,_height))  #resize image
    img = ImageTk.PhotoImage(original)
    Main_Window.create_image(0, 0, image=img, anchor="nw")


    Temp_y = (Coords[0]/Size[0])*_height
    Temp_x = (Coords[0]/Size[0])*_width


    V_line = Main_Window.create_line(Temp_y   , Temp_y-10, Temp_y   , Temp_y+10, fill="#ff0000", width=2)
    H_line = Main_Window.create_line(Temp_x-10, Temp_x   , Temp_x+10, Temp_x,    fill="#ff0000", width=2)

    Button_Save = tk.Button(Master_Window, text = "Save", command = Save, anchor = tk.N)
    Button_Save.configure(width = 10, background = "#FFFFFF")
    Button_Save.pack(side="right",  padx=10, ipadx=10, pady=7, ipady=0)
    
    QuitButton = quitButton(Master_Window)
    QuitButton.pack(side="right",  padx=10, ipadx=10, pady=7, ipady=0)

    Main_Window.bind("<Button 1>",getorigin)
    Master_Window.mainloop()
    
    return(Description,Centers)


# 
# ## Data analysis
#  
# **Plot_Colony** Receives and object Colony and plots its Area, Change in Radius, Change in Area and its Change in Color, 
#  

# In[ ]:


def Plot_Colony(Colony, x = 'Time', xlabel = 'Time (min)', props = 'default',  ylabels = 'default',  titles = 'default', **kwargs):
    '''
    Receives and object Colony and plots its Area, Change in Radius, Change in Area and its Change in Color, 
    
    Input:
    ---------------------
    Colony (Colony): 
        
    x (str):
        TimeDependent attribute from Colony Object.
        
    xlabel (str): 
        Label for x.
    
    color (str): 
        color of the plotted line.
    
    props (list):
        List of length 4, contains 4-time dependent attributes from Colony Object.
    
    ylabels (list): 
        Corresponding labels for pro
        
    titles (list): 
        Corresponding titles for plots.
        
    Returns:
    ---------------------
        Seaborn plots from python
    '''
    if not hasattr(Colony, 'Data'):
        Data = Colony.TimeDependent()
    else: 
        Data = Colony.Data
    
    if props ==  'default':
        props  = ['Area', 'C_Radius', 'C_Area', 'ColorInt']
    if ylabels ==  'default':
        ylabels= ['Area ($\mu$m^2)', '$\Delta$ Radius ($\mu$m/min)', '$\Delta$ area ($\mu$m^2)', 'Red Intensity (au)']
    if titles ==  'default':
        titles = ['Colony size {} (Area)'.format(Colony.Id),'Change in radius {}'.format(Colony.Id), 'Change in area {}'.format(Colony.Id),'Color intensity {}'.format(Colony.Id)]


    fig, ax =plt.subplots(2,2)
    ax_1, ax_2 , ax_3, ax_4 = ax[0,0], ax[1,0], ax[0,1], ax[1,1]
    
    ax_1 = sns.lineplot(x = x , y = props[0], data=Data, ax= ax_1, **kwargs)
    ax_2 = sns.lineplot(x = x , y = props[1], data=Data, ax= ax_2, **kwargs)
    ax_3 = sns.lineplot(x = x , y = props[2], data=Data, ax= ax_3, **kwargs)
    ax_4 = sns.lineplot(x = x , y = props[3], data=Data, ax= ax_4, **kwargs)
    
    ax_1.set(title = titles[0], ylabel=ylabels[0], xlabel=xlabel)
    ax_2.set(title = titles[1], ylabel=ylabels[1], xlabel=xlabel)
    ax_3.set(title = titles[2], ylabel=ylabels[2], xlabel=xlabel)
    ax_4.set(title = titles[3], ylabel=ylabels[3], xlabel=xlabel)
    
    
    
def Plot_Colony_beta(Df, col, color = 'blue'):
    '''
    g = sns.set(rc={'figure.figsize':(16,12)}, font_scale=1.2)


    Selected_Colony = col
    Trough_time = Df[Df.Colony == Selected_Colony]
    Distance = list(Trough_time.Distance)[0]

    fig, ax =plt.subplots(2,2)
    ax_1, ax_2 , ax_3, ax_4 = ax[0,0], ax[1,0], ax[0,1], ax[1,1]
    ax_1 = sns.lineplot(x = 'Time' , y = 'Area', data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_1)
    ax_1 = sns.scatterplot(x = 'Time' , y = 'Area', data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_1)
    ax_1.set(title = 'Colony Size', ylabel='Area ($\mu$m^2)', xlabel='Time (hrs.)')

    ax_2 = sns.lineplot(x = 'Time' , y = 'Growth_r' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_2)
    ax_2 = sns.scatterplot(x = 'Time' , y = 'Growth_r' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_2)
    ax_2.set(title = 'Change in radius', ylabel='$\Delta$ Radius ($\mu$m/min)', xlabel='Time (hrs.)')

    ax_3 = sns.lineplot(x = 'Time' , y = 'Growth' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_3)
    ax_3 = sns.scatterplot(x = 'Time' , y = 'Growth' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_3)
    ax_3.set(title = 'Change in area', ylabel='$\Delta$ area ($\mu$m^2)', xlabel='Time (hrs.)')

    ax_4 = sns.lineplot(x = 'Time' , y = 'Smooth_Red_Change' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_4)
    ax_4 = sns.scatterplot(x = 'Time' , y = 'Smooth_Red_Change' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_4)
    ax_4.set(title = 'Colony growth radius', ylabel='$\Delta$ Red Intensity (au)', xlabel='Time (hrs.)')

    print('Colony selected: {}\nDistance from the center: {} cm'.format(Selected_Colony, Distance/1000))
    '''
    ###Observe single Colonies
    g = sns.set(rc={'figure.figsize':(16,12)}, font_scale=1.2)


    Selected_Colony = col
    Trough_time = Df[Df.Colony == Selected_Colony]
    Distance = list(Trough_time.Distance)[0]

    fig, ax =plt.subplots(2,2)
    ax_1, ax_2 , ax_3, ax_4 = ax[0,0], ax[1,0], ax[0,1], ax[1,1]
    ax_1 = sns.lineplot(x = 'Time' , y = 'Area', data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_1)
    ax_1 = sns.scatterplot(x = 'Time' , y = 'Area', data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_1)
    ax_1.set(title = 'Colony Size', ylabel='Area ($\mu$m^2)', xlabel='Time (hrs.)')

    ax_2 = sns.lineplot(x = 'Time' , y = 'Growth_r' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_2)
    ax_2 = sns.scatterplot(x = 'Time' , y = 'Growth_r' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_2)
    ax_2.set(title = 'Change in radius', ylabel='$\Delta$ Radius ($\mu$m/min)', xlabel='Time (hrs.)')

    ax_3 = sns.lineplot(x = 'Time' , y = 'Growth' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_3)
    ax_3 = sns.scatterplot(x = 'Time' , y = 'Growth' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_3)
    ax_3.set(title = 'Change in area', ylabel='$\Delta$ area ($\mu$m^2)', xlabel='Time (hrs.)')

    ax_4 = sns.lineplot(x = 'Time' , y = 'Smooth_Red_Change' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_4)
    ax_4 = sns.scatterplot(x = 'Time' , y = 'Smooth_Red_Change' , data=Trough_time[Trough_time.Time < 1200], color = color , ax= ax_4)
    ax_4.set(title = 'Colony growth radius', ylabel='$\Delta$ Red Intensity (au)', xlabel='Time (hrs.)')

    print('Colony selected: {}\nDistance from the center: {} cm'.format(Selected_Colony, Distance/1000))


# 
# ## Classes     Experiment[Dish][Colony]
# 
# All classes have: 
# 
#   *  Slice_2_Min - Change from time slice to minutes
#   *  Min_2_Slice - Change from minutes to time slices
#   *  TimeIndependent - Observe time independent attributes, like max area, max growth, max color, etc.
#   *  TimeDependent -  Observe time dependent attributes, like area, growth, color
#   *  Id_2_str  - Change Id to string: "Col_[No]"
#   *  Id_2_int  - Change Id to Integer: N
# 
# **Colony** After initiated has 2 main methods: Grow (adds the new attributes into its inner lists) or Calculate (calculates color intensity, change from t(0) to t(1). 
# 
#         self.Interval  =  Interval
#         self.Id        =  int(Dict['Id'])
#         self.App_t     =  Dict['Slice']
#         self.Area      = [Dict['Area']]
#         self.Coords    = (Dict['X'],Dict['Y'])
#         self.Color     = [Dict['Color_R'  ],Dict['Color_G'  ],Dict['Color_B'  ]]
#         self.StdDev    = [Dict['StdDev_R'],Dict['StdDev_G'],Dict['StdDev_B']]
#         self.Last_t    =  Dict['Slice']
#         self.Minutes   = False
#         self.Smoothed  = False
#         self.str_Id    = 'Col_' in str(self.Id)
#     
# 
# **Dish** Contains colonies from each individual petri dish. Eventually will include functions to perform over all colonies.
# 
#         self.DishNo       = dish
#         self.Interval     = parameters['Interval']
#         self.Condition    = parameters['Conditions'][dish-1]
#         self.Perturbation = parameters['Perturbations'][dish-1]
#         self.DPI          = parameters['Resolution']
#         self.Center       = [(coord/316)*10000*self.DPI/800 for coord in parameters['Centers'][dish-1]]
#         self.Raw_Data     = ReadRawResults(pth, self.DishNo, Add_to_Id, reverse, Filter_Dupl)
#         self.Max_t        = int(max(self.Raw_Data.Slice))
#         
#         self.reverse      = reverse
#         self.Filter_Dupl  = Filter_Dupl
#         self.Last_t_filt  = Last_t_filt
#         self.Colonies     = {}
#         
#         #Flags
#         self.Read         = False
#         self.Minutes      = False
#         self.str_Id       = 'Col_' in str(self.Raw_Data.iloc[0]['Id'])
#         
# ** Experiment ** Contains a number of dishes
#         
#         self.Dishes     =  {'Dish_{}'.format(dishes):0} if type(dishes)== int else {'Dish_{}'.format(i):0 for i in dishes}
#         self.Pth        =  pth if pth[-1] == '/' else pth+'/'
#         self.Parameters =  ReadDescription(self.Pth+'Description.txt')
#         self.Col_No     =  0
#         self.smooth     = smooth
#         self.color      = color
#         self.Pol_N      = Pol_N
#         self.Minutes    = False
#         self.str_Id     = False
#         self.verbose    = verbose
# 
# 

# In[ ]:


#Class: Colony
class Colony():
    '''
    Class Colony: 
    '''
    def __init__(self, Dict, Interval = 10):
        self.Interval  =  Interval
        self.Id        =  int(Dict['Id'])
        self.App_t     =  Dict['Slice']
        self.Area      = [Dict['Area']]
        self.Coords    = (Dict['X'],Dict['Y'])
        self.Color     = [Dict['Color_R'  ],Dict['Color_G'  ],Dict['Color_B'  ]]
        self.StdDev    = [Dict['StdDev_R'],Dict['StdDev_G'],Dict['StdDev_B']]
        self.Last_t    =  Dict['Slice']
        self.Minutes   = False
        self.Smoothed  = False
        self.str_Id    = 'Col_' in str(self.Id)
    
    def __len__(self):        
        return(len(self.Area)) 
        

    def __iter__(self):
        self.iterCols = 0
        return self

    def __next__(self):
        if not hasattr(self, 'Data'):
            self.TimeDependent(write = True)
        
        x = np.array(self.Data)[self.iterCols]
        if self.iterCols < len(self)-1: 
            self.iterCols += 1
            return x
        raise StopIteration

    
    def Grow(self, Dict):
        self.Last_t    = Dict['Slice']
        self.Area      = self.Area + [Dict['Area']]
        self.Color     = np.vstack([self.Color     , [Dict['Color_R'  ], Dict['Color_G'  ], Dict['Color_B'  ]]])
        self.StdDev    = np.vstack([self.StdDev , [Dict['StdDev_R'], Dict['StdDev_G'], Dict['StdDev_B']]])


    def Calculate(self, smooth = False, color = 'Red', Pol_N = 2):
        '''
        Obtain
        '''
        self.Valid     = False if len(self) < Pol_N+2 else True  ## Colonies are only valid if they live for 2 time points
                                                                ## more than the smoothing window in the Savglov filter (Pol_N).
                
        if not self.Valid: 
            return()
        if (smooth and not self.Smoothed and self.Valid):
            if len(self) < 9:
                if (len(self)%2 == 0):
                    win = len(self)-1
                else:
                    win = len(self)
            else: 
                win = 9

            self.Area      = [val if val >= 0 else 0 for val in Savgol(self.Area, win, Pol_N)] #Removes negative values to be inputted
            self.Color     = np.array([Savgol(i, win, Pol_N) for i in self.Color.T]).T
            self.StdDev = np.array([Savgol(i, win, Pol_N) for i in self.StdDev.T]).T
            self.Smoothed  = True
            
        if not smooth:
            self.Radius    = [np.sqrt(i/np.pi) for i in self.Area]
            self.Color     = np.array([i for i in self.Color.T]).T
            self.StdDev = np.array([i for i in self.StdDev.T]).T
        
        
        self.Radius        = [np.sqrt(i/np.pi) for i in self.Area]
        self.ColorInt      = [Color_Intensity(RGB, color) for RGB in self.Color]

        self.C_Radius      =  Change(self.Radius)
        self.C_Area        =  Change(self.Area)
        self.C_ColorInt    =  Change(self.ColorInt)
    
        for att in ['Area', 'Radius', 'ColorInt', 'C_Area', 'C_Radius', 'C_ColorInt']:

            Max, Pos = ExtremaPos(list(self.__dict__[att]), _tuple=True)
            Name_1, Name_2 = ('Max_{}'.format(att),'Max_{}_t'.format(att))
            setattr(self, Name_1, Max)
            setattr(self, Name_2, Pos+self.App_t)
    
    def Slice_2_Min(self):
        '''
        Converts parameters with the "_t" suffix into minutes.
        '''
        if not self.Minutes:
            for prop in self.__dict__.keys():
                if '_t' in prop:
                    setattr(self, prop, self.__dict__[prop]*self.Interval)
            self.Minutes = True
                        
    def Min_2_Slice(self):
        '''
        Converts parameters with the "_t" suffix into minutes.
        '''
        if self.Minutes:
            for prop in self.__dict__.keys():
                if '_t' in prop:
                    setattr(self, prop, self.__dict__[prop]/self.Interval)
            self.Minutes = False
            
    def TimeIndependent(self):
        '''
        Returns all Time Independent Parameters and coordinates
            
        '''      
        if hasattr(self, 'Distance'):
            return(dict({i:self.__dict__[i] for i in self.__dict__.keys() if 'Max' in i}, **{'App_t':self.App_t, 'X':self.Coords[0],'Y':self.Coords[1], 'Distance':self.Distance, 'Id':self.Id}))
        else:
            return(dict({i:self.__dict__[i] for i in self.__dict__.keys() if 'Max' in i}, **{'App_t':self.App_t, 'X':self.Coords[0],'Y':self.Coords[1],'Id':self.Id}))
            

    def TimeDependent(self, write = False):
        '''
        
        '''
        temp = []
        Names = []
        for att in self.__dict__:
            t = self.__dict__[att]
            if type(t) ==  np.ndarray or type(t) == list:
                if  att == 'Color' or att == 'StdDev':
                    t = pd.DataFrame(t)
                    Names += [att+'_R', att+'_G', att+'_B']
                else:
                    Names.append(att)
                t = pd.DataFrame(t)
                temp.append(t)
        if self.Minutes:
            temp.append(pd.DataFrame(np.arange(self.App_t/self.Interval, (self.App_t+len(self)))*self.Interval))
        else:
            temp.append(pd.DataFrame(np.arange(self.App_t, (self.App_t+len(self)))))
        temp = pd.concat(temp, axis=1)
        temp.columns = Names+['Time']
        if write:
            self.Data = temp
        else:
            return(temp)
    
    def Id_2_str(self):
        if not self.str_Id:
            self.Id = 'Col_{}'.format(int(self.Id))
            self.str_Id = True
    def Id_2_int(self):
        if self.str_Id:
            self.Id = int(self.Id[4:])
            self.str_Id = False
            
class Dish():
    def __init__(self, pth, dish, parameters, No_Slices = 0, Add_to_Id = 0, Last_t_filt = True, reverse = True, Filter_Dupl = True):        
        #Parameters read from Description.txt
        self.DishNo       = dish
        self.Interval     = parameters['Interval']
        self.Condition    = parameters['Conditions'][dish-1]
        self.Perturbation = parameters['Perturbations'][dish-1]
        self.DPI          = parameters['Resolution']
        self.Center       = [(coord/316)*10000*self.DPI/800 for coord in parameters['Centers'][dish-1]]
        self.Raw_Data     = ReadRawResults(pth, self.DishNo, No_Slices,  Add_to_Id, reverse, Filter_Dupl)
        self.Max_t        = int(max(self.Raw_Data.Slice))
        self.No_Slices    = No_Slices
        
        self.reverse      = reverse
        self.Filter_Dupl  = Filter_Dupl
        self.Last_t_filt  = Last_t_filt
        self.Colonies     = {}
        
        #Flags
        self.Read         = False
        self.Minutes      = False
        self.str_Id       = 'Col_' in str(self.Raw_Data.iloc[0]['Id'])
        
    
    def __len__(self):  
        if self.Read:
            return(len(self.Colonies))
        return(len(set(self.Raw_Data['Id'])))
        
        
    def __iter__(self):
        return iter(self.Colonies.values())


    def addConditions(self):
        self.Raw_Data['Conditions'   ] = self.Condition
        self.Raw_Data['Perturbations'] = self.Perturbation

    
    def Add_Colony(self, Dict):
        if Dict['Id'] not in self.Colonies:
            self.Colonies[Dict['Id']] = Colony(Dict, Interval = self.Interval)
            self.Colonies[Dict['Id']].Distance = np.sqrt((self.Center[0]-Dict['X'])**2+(self.Center[1]-Dict['Y'])**2)
        else:
            self.Colonies[Dict['Id']].Grow(Dict)
    
        
    def Id_2_str(self):
        if self.str_Id:
            print('Ids are already converted to strs')
        else:
            self.Raw_Data['Id'] = [str('Col_{}'.format(_id)) for _id in self.Raw_Data['Id']]
            self.Colonies = {'Col_'+str(int(_id)):self.Colonies[_id] for _id in self.Colonies}
            
        for col in self.Colonies: 
            self.Colonies[col].Id_2_str()
        
        self.str_Id = True
        
            
    def Id_2_int(self): 
        if not self.str_Id:
            print('Ids are already converted to integers')
        else:
            self.Raw_Data['Id'] = [int(_id[4:]) for _id in self.Raw_Data['Id']]
            self.Colonies = {int(_id[4:]):self.Colonies[_id] for _id in self.Colonies}
            
        for col in self.Colonies: 
            self.Colonies[col].Id_2_int()
            
        self.str_Id = False
    
    def ReadColonies(self, smooth = False, color = 'Red', Pol_N = 2):
        if (self.Read != True | (smooth != True or color!= 'Red' or Pol_N != 2)):
            for i,col in self.Raw_Data.iterrows(): 
                self.Add_Colony(col)

            for col in self.Colonies.keys():
                self.Colonies[col].Calculate(smooth, color, Pol_N)
            self.Colonies = {_id:self.Colonies[_id] for _id in self.Colonies if self.Colonies[_id].Valid}
            if (self.Last_t_filt):
                self.Colonies = {_id:self.Colonies[_id] for _id in self.Colonies if int(self.Colonies[_id].Last_t) == self.Max_t}
            self.Read = True

    def TimeDependent(self, save = False):
        if not self.Read:
            self.ReadColonies()
            self.Read = True
        T_dep = []
        for col in self:
            temp = col.TimeDependent()
            temp['Id'] = col.Id
            T_dep.append(temp)
        T_dep = pd.concat(T_dep)
        T_dep.index = range(T_dep.shape[0])

        if save: 
            T_dep.to_csv(save)
        return(T_dep)

    def TimeIndependent(self, save = False):
        T_Independent = {}

        if not self.Read:
            self.ReadColonies()
            self.Read = True
        
        for col in self:
            T_Independent[col.Id] = col.TimeIndependent()
        T_Independent = pd.DataFrame(T_Independent).T

        if save: 
            T_Independent.to_csv(save)
        return(T_Independent)
    
    
    def Slice_2_Min(self):
        if self.Minutes:
            print('Slice is already in minutes')
        else:
            self.Raw_Data['Slice'] = self.Raw_Data['Slice']*self.Interval
            for col in self.Colonies: 
                self.Colonies[col].Slice_2_Min()
        
        self.Minutes = True
        
            
    def Min_2_Slice(self): 
        if not self.Minutes:
            print('Slice is already marking timePoints')
        else:
            self.Raw_Data['Slice'] = self.Raw_Data['Slice']/self.Interval
            for col in self.Colonies: 
                self.Colonies[col].Min_2_Slice()
            
        self.Minutes = False
        
        
    
    def get(self, att):
        '''
        Retrieves a dictionary with the given attribute from all colonies contained in self.


        Returns: 
        ----------
            {'Col_1':att,
             'Col_2':att
                 ...
             'Col_n':att}

        '''
        return({col.Id:col.__dict__[att] for col in self})
    
    def Plot_All_Colonies(self, col = None):

        Coords = self.get('Coords')
        X = [(Coords[i][0]/1000) for i in Coords]
        Y = [(Coords[i][1]/1000) for i in Coords]

        g = sns.scatterplot(X,Y, label='All')
        if col:
            g  = sns.scatterplot(x=0, y = 1, Raw_Data=pd.DataFrame([np.array(col.Coords)/1000]), color = 'red', label=col.Id)
        g.set(title = 'Colony positions', ylabel = 'X (mm)', xlabel='Y (mm)')
        plt.show()
        
        
        
class Experiment():
    def __init__(self, pth, dishes = range(1,7), smooth = False, No_Slices = 0, color = 'Red', Pol_N = 2, verbose = True):
        
        self.Dishes     =  {'Dish_{}'.format(dishes):0} if type(dishes)== int else {'Dish_{}'.format(i):0 for i in dishes}
        self.Pth        =  pth if pth[-1] == '/' else pth+'/'
        self.Parameters =  ReadDescription(self.Pth+'Description.txt')
        self.Col_No     =  0
        self.smooth     = smooth
        self.color      = color
        self.Pol_N      = Pol_N
        self.Minutes    = False
        self.str_Id     = False
        self.verbose    = verbose
        self.No_Slices  = No_Slices
        
        
        for prop in self.Parameters:
            setattr(self, prop, self.Parameters[prop])
            
        for _dish in self.Dishes:
            if self.verbose:
                print('Reading {}'.format(_dish))
            tmp = Dish(self.Pth, int(_dish[5:]), self.Parameters, No_Slices = self.No_Slices, Add_to_Id=self.Col_No)
            tmp.ReadColonies(smooth = self.smooth, color = self.color, Pol_N = self.Pol_N)
            self.Dishes[_dish] = tmp
            self.Col_No += len(tmp)

    def __iter__(self):
        return iter(self.Dishes.values())
    
    def __len__(self):  
        return len(self.Dishes)
    
    def Slice_2_Min(self):
        if self.Minutes:
            print('Slice is already in minutes')
        else:
            for dish in self:
                dish.Slice_2_Min()
        self.Minutes = True
        
    def Min_2_Slice(self):
        if not self.Minutes:
            print('Slice is already marking timePoints')
        else:
            for dish in self:
                dish.Min_2_Slice()
        self.Minutes = False
        
    def TimeDependent(self, save = False):
        T_dep = []
        for dish in self.Dishes: 
            tmp = self.Dishes[dish].TimeDependent()
            tmp['Dish'] = dish[5:]
            tmp['Condition'] = self.Parameters['Conditions'][int(dish[5:])-1]
            T_dep.append(tmp)
        T_dep = pd.concat(T_dep)
        T_dep.index  = range(T_dep.shape[0])
        
        if save: 
            T_dep.to_csv(save)
        return(T_dep)
        
    def TimeIndependent(self, save = False):        
        T_Ind = []
        for dish in self.Dishes: 
            tmp = self.Dishes[dish].TimeIndependent()
            tmp['Dish'] = dish[5:]
            tmp['Condition'] = self.Parameters['Conditions'][int(dish[5:])-1]
            T_Ind.append(tmp)
        T_Ind = pd.concat(T_Ind)
        T_Ind.index  = range(T_Ind.shape[0])
        if save: 
            T_Ind.to_csv(save)
        return(T_Ind)

    def Colonies(self):
        return([col for dish in self for col in dish])
    
    def get(self, att):
        return({col.Id:col.__dict__[att] for dish in self for col in dish if hasattr(col, att)})
    

