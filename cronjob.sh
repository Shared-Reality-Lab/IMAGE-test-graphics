#!/bin/bash

cd /home/rianad/test_graphics 
cd /home/rianad/test_graphics ; echo | date >> /home/rianad/test_graphics/diff.txt
cd /home/rianad/test_graphics ; var=$(./testset.py -t daily -d --daily)
echo $var >> /home/rianad/test_graphics/diff.txt

sub="Changes"

if [[ $var == *"$sub"* ]];
then
    echo "Changes occured"
else
    echo "No changes"
fi