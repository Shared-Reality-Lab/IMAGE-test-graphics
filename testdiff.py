#!/usr/bin/env python3
import sys
import getopt
import os
import json
import pathlib
import argparse
from datetime import datetime
import requests
#from PIL import Image

#can easily modify this to compare more than 2 time stamps in a directory, except what would we be comparing?
#every single file compared to each other?


#identifies differences for graphics for 2 different time stamps
# -n specifies the number of the directory
# if -n flag is not provided, then iterates through the entire directory to find directories that have that timestamp
# -t followed by 2 or more time stamps
# if all arguments aren't present, it returns an error

#creating parsers for arguments
parser = argparse.ArgumentParser()

parser.add_argument("-n", type=int, nargs=1, help ="-t followed by two time stamps (m_d_Y_H_M_S)")
parser.add_argument("-t", required=True, nargs=2, help = "(optional) -n followed by the integer number of the directory where the graphic is stored. If not provided, then compares all graphics that have the 2 time stamps")
args = parser.parse_args()

timestamps= args.t
outputfiles = []
for time in timestamps:
        outputfiles.append("output_"+time+".json")

file_name=[]
outputs=["a","b"]
if args.n:
    directories = args.n
    file = f'{directories[0]:04d}'
    f = os.path.join("photos", file)
    file_name.append(f)
    if not os.path.exists(f):
        assert False, "directory not found"
   
    outputs[0]=os.path.join(f,outputfiles[0])
        
    outputs[1]=os.path.join(f,outputfiles[1])
    if not (os.path.isfile(outputs[0]) and os.path.isfile(outputs[1])):
        assert False, "both timestamps do not exist in the directory"

else:
    
    for file in os.listdir("photos"):
        f = os.path.join("photos", file)
       
        outputs[0]=os.path.join(f,outputfiles[0])
        
        outputs[1]=os.path.join(f,outputfiles[1])
        if (os.path.isfile(outputs[0]) and os.path.isfile(outputs[1])):
            file_name.append(f)
    if not file_name:
        assert False, "no directory exists with both time stamps"
print(file_name)

for file1 in file_name:
    preprocessors = {}
    outputs[0] = os.path.join(file1,outputfiles[0])
    outputs[1] = os.path.join(file1,outputfiles[1])
    j = open(outputs[0])
    k = open(outputs[1])
    data0 = json.load(j)
    data1 = json.load(k)
    preprocessors[outputs[0]] = data0["preprocessors"]
    preprocessors[outputs[1]] = data1["preprocessors"]
    #TODO:  rather than just printing both outputs, better to use the unix `diff`
    #        command to hilight the actual differences
    print("for "+file1+":")
    if (preprocessors[outputs[0]] is not (preprocessors[outputs[1]])):
        print("difference found")
        print("preprocessor output for " + outputs[0] + " is")
        print(preprocessors[outputfiles[0]])
        print("preprocessor output for " + outputs[1] + " is")
        print(preprocessors[outputs[1]])
    else:
        print("same preprocessor outputs")
