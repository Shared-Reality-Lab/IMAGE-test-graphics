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

**to get a list of objects found for object detection**

Insert two time stamps and then use --od flag to specify which timestamp is which model. For example, if Azure was run at August 6 at 12:00am and YOLO was run at August 6 at 12:01am for graphic 35

`./testdiff.py -t 08_06_2022_00_00_00 08_06_2022_00_00_01 -n 35 --od Azure YOLO`

-d flag on testset.py will run a testdiff on the JSON that was just created and the next most recent JSON that was created for the graphic(s) (if it exists)

## azure.sh and yolo.sh:

azure.sh switches the docker compose for object detection from YOLO (default) to Azure
yolo.sh switches back through a restoreunstable

### example:

**to compare YOLO and Azure outputs for all indoor graphics**

```
./testset.py -t indoor
./azure.sh
./testset.py -t indoor -d
./yolo.sh
```

## llm-caption-test.py

Automated testing script for evaluating multimodal LLM descriptions of images from the IMAGE-test-graphics repository.

### Requirements

- Python 3.7+
- Ollama running locally (`ollama serve`)
- Internet connection (for GitHub API access)

### Installation

```bash
pip install requests pandas pillow
```

### Usage

```bash
python llm-caption-test.py
```

### Configuration

### Models
Edit the `MODELS` list in the script with model names and temperature settings:
```python
MODELS = [
    ("gemma3:12b", 0.0),
    ("gemma3:12b", 1.0),          
    ("llama3.2-vision:latest", 0.0),
    ("llama3.2-vision:latest", 1.0)
]
```

### Other Parameters
- **Prompt**: `PROMPT` parameter is applied to all models
- **Image size**: Modify `max_size` in `image_to_base64()` (default: 2048x2048)
- **API endpoint**: Update `url` in `run_ollama_model()` if not using localhost:11434
- **Image formats**: Add to `IMAGE_EXTENSIONS` set for other formats

### Output Files

1. **llm_test_results.csv** - Main results with columns:
   - `folder`: Folder number (0000-0067)
   - `filename`: Original image filename
   - `image`: HTML-embedded thumbnail
   - Model description columns (e.g., "llama3.2-vision:latest (t=0.0)")

2. **llm_test_results.html** - Formatted HTML view with embedded images

3. **intermediate_results.csv** - Auto-saved every 5 images (backup)

### Notes

- Processes 68 folders (0000-0067) from Shared-Reality-Lab/IMAGE-test-graphics
- Images are resized to max 2048x2048
- 1-second delay between model calls to avoid overload
- Handles various image formats (JPG, JPEG, PNG, GIF, BMP, WEBP)
- Error handling for missing images or API failures


