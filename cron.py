#!/usr/bin/env python3
import os

os.system("cd /home/rianad/test_graphics")
os.system("cd /home/rianad/test_graphics ; echo | date >> /home/rianad/test_graphics/diff.txt")
os.system("cd /home/rianad/test_graphics ; ./testset.py -t daily -d --daily >> /home/rianad/test_graphics/diff.txt")



