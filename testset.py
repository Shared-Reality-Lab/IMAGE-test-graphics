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
import base64
import uuid
import mimetypes
#if no arguments then the entire testset is included

# arguments:
# -t followed by a comma or space seperated list of tags
# -n followed by the directory number of the graphic(s) (eg. 6, 0006, 06, etc) space seperated list
# -s followed by u, unicorn, p, pegasus to specify the server we'd run graphic on
# -min for the minimum size in bytes
# -max for maximum size in bytes
# -r followed by true or false, or t or f

#filters for things like min size, number, regression and tags work on an AND basis so all the filter/requirements must be met
#the list of tags is on an OR basis, so at least one of the tags in the argument must be in the json

# if no server specified, defaults to unicorn?

# MUST have some argument, or returns error


# ask: call request to unicorn server would the server return preprocessor output?
# or any other way to get the preprocessor output

# parsing through arguments


parser = argparse.ArgumentParser()

parser.add_argument("-n", type=int, nargs='+')
parser.add_argument("--min", type=int)
parser.add_argument("--max", type=int)
parser.add_argument("-t", nargs='+')

parser.add_argument("-s")
parser.add_argument("-r")

args = parser.parse_args()

#default filters
max_size = -1
min_size = -1
tags_needed = []
graphics = []
server = ""
regressionpreference = False

#list of jsons that need to be parsed through
jsons = []


# assigning server if argument entered, else default is unicorn
if args.s:
    answer = args.s.lower()
    if answer in ["u", "unicorn"]:
        server = "https://unicorn.cim.mcgill.ca/image/render/preprocess"
    elif answer in ["p", "pegasus"]:
        server = "https://image.a11y.mcgill.ca/render/preprocess"
    else:
        assert False, "invalid server"
else:
    server = "https://unicorn.cim.mcgill.ca/image/render/preprocess"

#tags can be seperated by commas, spaces, or both
if args.t:
    
    tagscomma = args.t
    for tag in tagscomma:
        tagspace = tag.split(',')
        for word in tagspace:
            tags_needed.append(word.lower())
#print(tags_needed)
if args.n:
    graphics = args.n
#keeps track of regression
if args.r:
    answer = args.r.lower()
    if answer in ["t", "true"]:
        regression = True
        regressionpreference = True
    elif answer in ["f", "false"]:
        regression = False
        regressionpreference = True
    else:
        assert False, "invalid regression"

#assigning min and max size
if args.min:
    min_size = args.min
if args.max:
    max_size = args.max

#iterating through files in directory, checking if the filter is relevant, and then checking the 
#description json to verify that the photo meets the requirements
for file in os.listdir("photos"):
    
    f = os.path.join("photos", file)
    filenumber = int(f.replace("photos/", ""))
    h = pathlib.Path(os.path.join(f, "description.json"))

    if os.path.isdir(f):
        if h.exists():
            #print(h)
            isIncluded = True
            j = open(h)
            data = json.load(j)
            data["path"] = f
            if (len(tags_needed)!=0):
                isIncluded = False
                for item in data["tags"]:
                    if item in tags_needed:
                        isIncluded = True
            if(len(graphics)!=0):
                if filenumber not in graphics:
                    isIncluded = False

            if regressionpreference:
                if regression:
                    if data["regression"] is False:
                        isIncluded = False
                if not regression:
                     if data["regression"] is True:
                            isIncluded = False
            if max_size > 0:
                if data["bytes"] > max_size:
                    isIncluded = False
            if min_size > 0:
                if data["bytes"] < min_size:
                    isIncluded = False
            
            if isIncluded:
                jsons.append(data)
               # print(filenumber)



#print(len(jsons))

#creating the output json
for item in jsons:
    path = item["path"]

   
    jsondict = {}
   
    jsondict["url"] = item["url"]
    jsondict["image"] = item["image"]
    
    date_time = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    file_name = "output"+date_time+".json"
    jsondict["time"] = date_time

    photo = item["image"]
    photoname = os.path.join(path, photo)
    print (photoname)
    
   # try:
      #  im=Image.open(photoname)
        
 #   except IOError:
    #   assert False, "not an image file"

    with open(photoname, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
    mime_type = mimetypes.guess_type(photoname)
    
    jsoninput = {}
    jsoninput["request_uuid"] = str(uuid.uuid4())

    today = datetime.now()

    seconds = today.timestamp()
    jsoninput["timestamp"] = int(seconds)
    jsoninput["image"] = "data:{};base64,{}".format(mime_type[0], b64_string.decode())
   
    jsoninput["dimensions"]=item["dimensions"]
    jsoninput["context"]=""
    jsoninput["language"]="en"
    jsoninput["capabilities"] = []
    jsoninput["renderers"] = [ "ca.mcgill.a11y.image.renderer.Text", "ca.mcgill.a11y.image.renderer.SimpleAudio", "ca.mcgill.a11y.image.renderer.SegmentAudio" ]
    jsoninput["preprocessors"] = {}
   
    #preprocessor_output = requests.post(url=server, json = json.dumps(jsoninput))
   
    #print(preprocessor_output)

    jsondict["preprocessors"] = ""#preprocessor_output
    #print(server)
    #print(preprocessor_output.json())
    #print(requests.status_codes)
    h = os.path.join(path, file_name)

    jsondict["handlers"] = ""
    
    with open(h,'x') as jsonFile:
        #jsonFile.write('\n')
        json.dump(jsondict,jsonFile, indent=2)
      
      
      
      
       # for items in jsondict:
          #  json.dump(items, jsonFile)
           # jsonFile.write('\n')
    

