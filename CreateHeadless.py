#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import PetriScanner2 as ps

Finisished = False  
msg = '''==============================\n===========  HELP  ===========\n==============================\n    This function creates a bat file that once you click on it, will allow you to run ImageJ in a headless manner.
    
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
		path Path/To/Experiment/ --detect_t 270 --r_Avg_col_size 1.68 –-Type Otsu --Rmv_Bkgrnd true --Color_correction true –verbose true --watershed true\n\
==============================\n\
==============================\n\
==============================
'''

Input = input('Welcome to PetriScanner\nIf no flags are given, defaults are chosen, enter your command:\n\tExample of command:\n\tpath C:/Users/USER/Path/to/Experiment\n\n\t').strip()
if (Input.lower() == '--help') or (Input.lower() == '-help') or (Input.lower() == '--h'):
    print(msg)

while not Finisished:
    try:
        Arguments = dict({i.split(' ')[0].lower():i.split(' ')[1].lower() for i in ' '.join(Input.split()).split('-') if 'path' not in i }, 
                 **{i.split(' ')[0].lower():i.split(' ')[1] if i.split(' ')[1][-1] == '/' else i.split(' ')[1]+'/' for i in ' '.join(Input.split()).split('-') if 'path' in i})

        if 'path' not in Arguments:
            print('ERROR: "path" is to declared.\n\n\t')
            break
                
        if not os.path.exists(Arguments['path']):
            print('ERROR:\tThe specified path does not exist.\n\n\t')
            break
        else:
            ps.CreateRunner(**Arguments)
            if 'help' not in Input.lower():
                Finisished = True
    except IndexError: 
        if 'help' in Input.lower():
            Input = input('Please rewrite the command\n\tIf you are having trouble you can type --help\n\n\t').strip()
            
        else:
            Input = input('Command is not written properly or its missing arguments.\nPlease rewrite the command\n\tIf you are having trouble you can type --help.\n\n\t').strip()
            
        if (Input.lower() == '--help') or (Input.lower() == '-help') or (Input.lower() == '--h'):
            print(msg)

