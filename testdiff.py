#!/usr/bin/env python3
import sys
import getopt
import os
import json
import pathlib
import argparse
from datetime import datetime
import requests
import difflib
from deepdiff import DeepDiff
import re

#identifies differences for graphics for 2 different time stamps
# -n specifies the number of the directory
# if -n flag is not provided, then iterates through the entire directory to find directories that have that timestamp
# -t followed by 2 time stamps
# --preprocessor followed by the names of the preprocessors to compare. if not specified, compares all preprocessors.
# if -t arguments aren't present, it returns an error
# if -d flag, use for testing and save a file
# -- list flag just lists the preprocessors that changed instead of the changes followed by the number of changes

#changes boolean keeps track of if there has been a change

changes = False

#creating parsers for arguments

parser = argparse.ArgumentParser()

parser.add_argument("-n", type=int, nargs=1, help ="-t followed by two time stamps (m_d_Y_H_M_S)")
parser.add_argument("-t", required=True, nargs=2, help = "(optional) -n followed by the integer number of the directory where the graphic is stored. If not provided, then compares all graphics that have the 2 time stamps")
parser.add_argument("--preprocessor", nargs = '+', help = "followed by a list of the preprocessors for which we want to see the diffs, everything else will be excluded")
parser.add_argument("--od", nargs=2)
parser.add_argument("-d", action = "store_true", help = "use instead of -t flag, uses 2 most recent timestamps in directory")
parser.add_argument("--list", action="store_true", help = "followed by a list of the preprocessors for which we want to see the diffs, everything else will be excluded")


args = parser.parse_args()

#if --preprocessor was specified, keeps track of which ones need to compare in a list, toparse
toparse = []
preprocessorspecified = False
if args.preprocessor:
    preprocessorspecified = True
    for item in args.preprocessor:
        toparse.append("ca.mcgill.a11y.image.preprocessor." + item)
    

#ensures 2 different time stampes
if args.t:
    if args.t[0] == args.t[1]:
        print("please enter two different time stamps to compare")
        sys.exit(1)
        
    #keeps track of which files to compare
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
        print("directory not found")
        sys.exit(2)
   
    outputs[0]=os.path.join(f,outputfiles[0])
        
    outputs[1]=os.path.join(f,outputfiles[1])
    if not (os.path.isfile(outputs[0]) and os.path.isfile(outputs[1])):
        print("both timestamps do not exist in the directory")
        sys.exit(3)


else:
    
    for file in os.listdir("photos"):
        f = os.path.join("photos", file)
       
        outputs[0]=os.path.join(f,outputfiles[0])
        
        outputs[1]=os.path.join(f,outputfiles[1])
        if (os.path.isfile(outputs[0]) and os.path.isfile(outputs[1])):
            file_name.append(f)
    if not file_name:
        print( "no directory exists with both time stamps")
        sys.exit(4)

finalfile = {}
#compares files for each file in the list file_name
for file1 in file_name:
    preprocessors = {}
    outputs[0] = os.path.join(file1,outputfiles[0])
    outputs[1] = os.path.join(file1,outputfiles[1])
    j = open(outputs[0])
    k = open(outputs[1])
    data0 = json.load(j)
    data1 = json.load(k)
    data0.pop("time")
    data1.pop("time")

    pre1 = data0["preprocessors"]
    pre2 = data1["preprocessors"]
    dicttofile = {}
    if args.preprocessor:
        for preprocessor in toparse:
            x = (DeepDiff(pre1[preprocessor], pre2[preprocessor]))
            if "values_changed" in x:
                changes = True
                j = x["values_changed"]
                for a in j:
                    dicttofile[a] = j[a]
       

    else:
        x = (DeepDiff(data0["preprocessors"], data1["preprocessors"]))
        if "values_changed" in x:
            
            j = x["values_changed"]
            changes = True
            for a in j:
                if args.list:
                    pattern = r"\['(.*?)'\]"
                    # Find all matches of the pattern in the input string
                    matches = re.findall(pattern, a)
                    # The preprocessor name is the first match
                    preprocessor_name = matches[0]
                    
                    if preprocessor_name in dicttofile:
                        dicttofile[preprocessor_name] = dicttofile[preprocessor_name] + 1
                    else:
                        dicttofile[preprocessor_name] = 1
                else:
                    dicttofile[a] = j[a]

    if changes:
        print(file1)
        for thing in dicttofile:
            print(thing)
            print(dicttofile[thing])    
    finalfile[file1] = dicttofile
datepath = "/var/docker/image/testing/diffs/"
now = datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")

datepath = datepath + current_time + ".txt"
if args.d:
    with open(datepath, 'w') as json_file:
    # Write the dictionary to the file in JSON format
        json.dump(finalfile, json_file)

if changes:
    print("Changes occured")


