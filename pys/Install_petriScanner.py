#!/usr/bin/env python
# coding: utf-8

import PetriScanner2 as ps
import os
try:
    os.path.exists(ps.Pth_2_ImageJ())
    ps.setupMacros()
except FileNotFoundError:
    print("ERROR\nAdd the correct path to: ../OurSoftware/defaults/pth_to_ImageJ.txt")