#!/bin/bash

cd /var/docker/image/IMAGE-test-graphics 
now=`date +"%m_%d_%Y"`
var=$(./testset.py -s p -t daily -d --daily)

sub="Changes"

if [[ $var == *"$sub"* ]];
then
    echo "Changes occured"
    echo $var >> /var/docker/image/testing/$now.txt
    

fi
