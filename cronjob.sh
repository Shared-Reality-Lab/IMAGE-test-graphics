#!/bin/bash

cd /home/rianad/test_graphics 
now=`date +"%m_%d_%Y"`
cd /home/rianad/test_graphics ; var=$(./testset.py -t daily -d --daily)


sub="Changes"

if [[ $var == *"$sub"* ]];
then
    echo "Changes occured"
    echo $var >> /var/docker/atp/testing/$now.txt
    

fi