#!/usr/bin/env python3
import matplotlib
import numpy as np
import matplotlib
import pandas
import wordcloud
from wordcloud import WordCloud
import os
import json
import pathlib

import PIL
from PIL import Image
import matplotlib.pyplot as plt
c = 0
tags = {}
for file in os.listdir("photos"):
    f = os.path.join("photos", file)
    h = pathlib.Path(os.path.join(f, "description.json"))
    if os.path.isdir(f):
        if h.exists():
            j = open(h)
            data = json.load(j)
            list = data["tags"]
            for word in list:
                if word not in tags:
                    tags[word] = 1
                else :
                    tags[word] = tags[word] + 1

            
        #print()
        #json_object = json.loads("input.json")
       # print(json_object["tags"])
print(tags)

wc = WordCloud(background_color="white",width=1000,height=1000).generate_from_frequencies(tags)
#print(data)

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()
wc.to_file('wordcloud.png')
