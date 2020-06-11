#!/usr/bin/env python
# coding: utf-8

import PetriScanner2 as ps
import os 

pth_in = input('Enter the path to the folder containing the experiment to be analized:\n\t')
pth_in = pth_in+'/' if pth_in[-1:] != '/' else pth_in
exist = os.path.exists(pth_in)
while not exist:
    pth_in = input('The path that you entered is incorrect, try again:\n\t')
    pth_in = pth_in+'/' if pth_in[-1:] != '/' else pth_in
    exist = os.path.exists(pth_in)
    
Exp = ps.Experiment(pth_in, smooth = False)
Exp.TimeDependent  (save = pth_in+'TimeDependent.csv')
Exp.TimeIndependent(save = pth_in+'TimeIndependent.csv')