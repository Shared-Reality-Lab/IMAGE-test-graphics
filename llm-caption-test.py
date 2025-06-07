#!/usr/bin/env python3
"""
Multimodal LLM Test Script for evaluating image descriptions

DISCLAIMER:
This script is written to run on the local machine with Ollama installed.
You may need to adjust the Ollama API endpoint if you are using a different setup.
Refer to README.md for details on how to set up and run this script.
"""

import base64
import requests
import pandas as pd
from pathlib import Path
import subprocess
from io import BytesIO
from PIL import Image
import time
from typing import Dict, List, Tuple

# Configuration
GITHUB_REPO = "Shared-Reality-Lab/IMAGE-test-graphics"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

# Model configurations (name and temperature)
MODELS = [
    ("gemma3:12b", 0.0),
    ("gemma3:12b", 1.0),
    ("llama3.2-vision:latest", 0.0),
    ("llama3.2-vision:latest", 1.0)
]

PROMPT = '''Give a detailed description of the style, content,
and the most significant aspects of this image.
Answer with maximum one sentence.'''

# Image extensions to look for
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


def get_folder_contents(folder_num: str) -> List[Dict]:
    """Fetch the contents of a specific folder from GitHub"""
    url = f"{GITHUB_API_BASE}/photos/{folder_num}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contents of folder {folder_num}: {e}")
        return []


def find_image_in_folder(contents: List[Dict]) -> str:
    """Find the first image file in the folder contents"""
    for item in contents:
        if item['type'] == 'file':
            file_ext = Path(item['name']).suffix.lower()
            if file_ext in IMAGE_EXTENSIONS:
                return item['name']
    return None


def download_image(folder_num: str, filename: str) -> bytes:
    """Download an image from GitHub"""
    url = f"{GITHUB_RAW_BASE}/photos/{folder_num}/{filename}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {folder_num}/{filename}: {e}")
        return None


def image_to_base64(image_bytes: bytes, max_size: Tuple[int, int] = (2048, 2048)) -> str:
    """Convert image bytes to base64, optionally resizing"""
    try:
        # Open and potentially resize image
        img = Image.open(BytesIO(image_bytes))

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        # Convert to base64
        return base64.b64encode(buffer.read()).decode('utf-8')
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def run_ollama_model(model_name: str, temperature: float, image_base64: str,
                     prompt: str = PROMPT) -> str:
    """Run an ollama model on an image using the HTTP API"""
    try:
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"

        # Prepare the request payload
        payload = {
            "model": model_name,
            "prompt": prompt,
            "images": [image_base64],
            "options": {
                "temperature": temperature
            },
            "stream": False
        }

        # Make the API request
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Parse the response
        result = response.json()
        return result.get('response', 'No response generated')

    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
        return "Error: Ollama not running"
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error running ollama with {model_name} (t={temperature}): {e}")
        return f"HTTP Error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error running ollama: {e}")
        return f"Error: {str(e)}"


def create_html_image_cell(image_base64: str, filename: str) -> str:
    """Create an HTML cell with embedded image for the CSV"""
    return f'<img src="data:image/jpeg;base64,{image_base64}" alt="{filename}" style="max-width:200px; max-height:200px;">'


def main():
    """Main execution function"""
    print("Starting Multimodal LLM Test Script...")

    # Check if ollama API is available
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama API")
        print("Please make sure Ollama is running: ollama serve")
        return
    except Exception as e:
        print(f"Error checking Ollama API: {e}")
        return

    # Create results list
    results = []

    # Process each folder
    for i in range(68):  # 0000 through 0067
        folder_num = f"{i:04d}"
        print(f"\nProcessing folder {folder_num}...")

        # Get folder contents
        contents = get_folder_contents(folder_num)
        if not contents:
            print(f"Skipping folder {folder_num} - no contents found")
            continue

        # Find image file
        image_filename = find_image_in_folder(contents)
        if not image_filename:
            print(f"No image found in folder {folder_num}")
            continue

        print(f"Found image: {image_filename}")

        # Download image
        image_bytes = download_image(folder_num, image_filename)
        if not image_bytes:
            continue

        # Convert to base64
        image_base64 = image_to_base64(image_bytes)
        if not image_base64:
            continue

        # Create result row
        row = {
            'folder': folder_num,
            'filename': image_filename,
            'image': create_html_image_cell(image_base64, f"{folder_num}/{image_filename}")
        }

        # Run each model configuration
        for model_name, temperature in MODELS:
            column_name = f"{model_name} (t={temperature})"
            print(f"  Running {column_name}...")

            description = run_ollama_model(model_name, temperature, image_base64)
            row[column_name] = description

            # Small delay to avoid overwhelming the system
            time.sleep(1)

        results.append(row)

        # Save intermediate results every 5 images
        if len(results) % 5 == 0:
            save_results(results, "intermediate_results.csv")
            print(f"Saved intermediate results ({len(results)} images processed)")

    # Save final results
    save_results(results, "llm_test_results.csv")
    print(f"\nCompleted! Processed {len(results)} images.")
    print("Results saved to llm_test_results.csv")


def save_results(results: List[Dict], filename: str):
    """Save results to CSV file"""
    if not results:
        print("No results to save")
        return

    # Create DataFrame
    df = pd.DataFrame(results)

    # Reorder columns
    columns = ['folder', 'filename', 'image']
    for model_name, temperature in MODELS:
        column_name = f"{model_name} (t={temperature})"
        if column_name in df.columns:
            columns.append(column_name)

    df = df[columns]

    # Save to CSV (with HTML support for viewing)
    df.to_csv(filename, index=False, escapechar='\\')

    # Also save as HTML for easier viewing
    html_filename = filename.replace('.csv', '.html')
    html_content = df.to_html(escape=False, index=False)

    # Add some CSS for better formatting
    html_full = f"""
    <html>
    <head>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            td {{
                max-width: 300px;
                word-wrap: break-word;
            }}
            img {{
                display: block;
                margin: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Multimodal LLM Test Results</h1>
        {html_content}
    </body>
    </html>
    """

    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_full)

    print(f"Also saved HTML version to {html_filename}")


if __name__ == "__main__":
    # Optional: Install required packages
    print("Checking required packages...")
    required_packages = ['requests', 'pandas', 'pillow']

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.run(["pip", "install", package], check=True)

    main()
