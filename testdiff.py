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

#identifies differences for graphics for 2 different time stamps
# -n specifies the number of the directory
# if -n flag is not provided, then iterates through the entire directory to find directories that have that timestamp
# -t followed by 2 time stamps
# --preprocessor followed by the names of the preprocessors to compare. if not specified, compares all preprocessors.
# if -t arguments aren't present, it returns an error

#changes boolean keeps track of if there has been a change

changes = False

#creating parsers for arguments

parser = argparse.ArgumentParser()

parser.add_argument("-n", type=int, nargs=1, help ="-t followed by two time stamps (m_d_Y_H_M_S)")
parser.add_argument("-t", required=True, nargs=2, help = "(optional) -n followed by the integer number of the directory where the graphic is stored. If not provided, then compares all graphics that have the 2 time stamps")
parser.add_argument("--preprocessor", nargs = '+', help = "followed by a list of the preprocessors for which we want to see the diffs, everything else will be excluded")
parser.add_argument("--od", nargs=2)

args = parser.parse_args()

#if --preprocessor was specified, keeps track of which ones need to compare in a list, toparse
toparse = []
preprocessorspecified = False
if args.preprocessor:
    preprocessorspecified = True
    for item in args.preprocessor:
        toparse.append("ca.mcgill.a11y.image.preprocessor." + item)
    

#ensures 2 different time stampes

if args.t[0] == args.t[1]:
    assert False, "please enter two different time stamps to compare"
    
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

  #  pre1 = json.loads(((data0["preprocessors"]).replace("contentCategoriser\"", "contentCategoriser"))[:-1])
  #  pre2 = json.loads(((data1["preprocessors"]).replace("contentCategoriser\"", "contentCategoriser"))[:-1])
    pre1 = data0["preprocessors"]
    pre2 = data1["preprocessors"]
    if not args.od:
        if not args.preprocessor:
            for key in pre1:
                if not pre1[key] == pre2[key]:
                    print(key)
                    print(pre1[key])
                    print(key)
                    print(pre2[key])
                    changes = True
        else:
            for key in toparse:
                if key not in pre1:
                    print(key + " not a preprocessor")
                else:    
                    if not pre1[key] == pre2[key]:
                        print(key)
                        print(pre1[key])
                        print(key)
                        print(pre2[key])
                        changes = True
    else:
        print(args.od[0])
        
        
        odlist = ((pre1["ca.mcgill.a11y.image.preprocessor.objectDetection"]))["objects"]
        lista=[]
        dicta = {}

        for dict in odlist:
            lista.append(dict["type"])
            if dict["type"] in dicta:
                dicta[dict["type"]] = dicta[dict["type"]] + 1
            else:
                dicta[dict["type"]] = 1
        #print(lista)
        print(dicta)
        
        print(args.od[1])
        odlist = ((pre2["ca.mcgill.a11y.image.preprocessor.objectDetection"]))["objects"]
        listb=[]
        dictb={}
        for dict in odlist:
            listb.append(dict["type"])
            if dict["type"] in dictb:
                dictb[dict["type"]] = dictb[dict["type"]] + 1
            else:
                dictb[dict["type"]] = 1
        #print(listb)
        print(dictb)




if changes:
    print("Changes occured")


