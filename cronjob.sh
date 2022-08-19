#!/bin/bash

cd /home/rianad/test_graphics 
cd /home/rianad/test_graphics ; echo | date >> /var/docker/atp/testing/diff.txt
cd /home/rianad/test_graphics ; var=$(./testset.py -t daily -d --daily)
echo $var >> /var/docker/atp/testing/diff.txt

sub="Changes"

if [[ $var == *"$sub"* ]];
then
    echo "Changes occured"
    

fi