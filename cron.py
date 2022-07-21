#!/usr/bin/env python3
import os

os.system("echo | date >> diff.txt")
os.system("./testset.py -t daily -d --daily >> diff.txt")
