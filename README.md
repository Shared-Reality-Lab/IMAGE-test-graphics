# IMAGE-test-graphics
Scripts and graphics used for ongoing testing of IMAGE

Scripts are used to iterate through the graphics, get output from the server, and compare outputs.

## testset.py:
Iterates through collection of graphics and builds a testset based on specified flags, sends a POST request for each of these graphics, writes the output to a timestamped JSON file. Default server is unicorn if not specified.

### examples:

**to iterate through the entire test set on pegasus:**

` ./testset.py -s pegasus `

**to iterate through graphics that are larger than 1000000 bytes and are tagged as "outdoor":**

` ./testset.py --minBytes 1000000 -t outdoor `

## testdiff.py:
Compares preprocessor output for any two JSON files.

### examples:

**to compare the output from August 6 2022 at midnight and August 7 2022 at midnight for all graphics which were run at that time:**

` ./testdiff.py -t 08_06_2022_00_00_00 08_07_2022_00_00_00 `, output will be a list of all graphics that have both timestamps, plus any differences

**to compare the output from August 6 2022 at midnight and August 7 2022 at midnight for graphic 35:**

` ./testdiff.py -t 08_06_2022_00_00_00 08_07_2022_00_00_00 -n 35 `


**to compare the grouping, sorting, and semantic segmentation output from August 6 2022 at midnight and August 7 2022 at midnight for graphic 35:**

` ./testdiff.py -t 08_06_2022_00_00_00 08_07_2022_00_00_00 -n 35 --preprocessor grouping sorting semanticSegmentation`

-d flag on testset.py will run a testdiff on the JSON that was just created and the next most recent JSON that was created for the graphic(s) (if it exists)

## azure.sh:

azure.sh switches the docker compose for object detection from YOLO (default) to Azure

### example:

**to compare YOLO and Azure outputs for all indoor graphics**

```
./testset.py -t indoor
./azure.sh
./testset.py -t indoor -d
```



