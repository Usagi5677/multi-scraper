# Multi-Scraper
scrapes files (jpg, png, gif, webm) from website

<div align="center">

  [<img src="gradio.svg" alt="gradio" width=300>](https://gradio.app)<br>
  <em>Build & share delightful machine learning apps easily</em>

  [![gradio-backend](https://github.com/gradio-app/gradio/actions/workflows/backend.yml/badge.svg)](https://github.com/gradio-app/gradio/actions/workflows/backend.yml)
  [![gradio-ui](https://github.com/gradio-app/gradio/actions/workflows/ui.yml/badge.svg)](https://github.com/gradio-app/gradio/actions/workflows/ui.yml)  
  [![PyPI](https://img.shields.io/pypi/v/gradio)](https://pypi.org/project/gradio/)
  [![PyPI downloads](https://img.shields.io/pypi/dm/gradio)](https://pypi.org/project/gradio/)
  ![Python version](https://img.shields.io/badge/python-3.8+-important)
  [![Twitter follow](https://img.shields.io/twitter/follow/gradio?style=social&label=follow)](https://twitter.com/gradio)

  [Website](https://gradio.app)
  | [Documentation](https://gradio.app/docs/)
  | [Guides](https://gradio.app/guides/)
  | [Getting Started](https://gradio.app/getting_started/)
  | [Examples](demo/)
  | [中文](readme_files/zh-cn#readme)
</div>


This Python script allows you to scrape images from various websites such as Instagram, Reddit, 4channel, Warosu, and Desuarchive. The script uses the Chrome browser for scraping and requires certain dependencies to be installed.

## Installation

Before using the image scraper, please make sure you have the following prerequisites:

- Python 3.x installed on your system
- Chrome browser (if not using headless option, ensure that Chrome is closed)
- Google Chrome Driver compatible with your Chrome browser version
- Download the appropriate Chrome Driver from [https://sites.google.com/a/chromium.org/chromedriver/downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads)

To install the required Python packages, run the following command:

```
pip install -r requirements.txt
```

## Usage

To use the image scraper, execute the `main.py` script with the following command:

```
python app.py
```

### Options

The script provides several options that can be specified via command-line arguments or within the script file itself.

- `--injected`: Enable this option to handle websites that inject their content during the initial page load. The script will wait until the page is fully loaded before scraping images. By default, this option is disabled.

- `--max-images`: Specify the maximum number of images you want to scrape from the website. This limits the number of images retrieved. If not specified, all available images will be scraped.

- `--bulk`: Enable this option to scrape images from multiple URLs provided in a text file. The URLs in the text file should be separated by commas. The file path must be provided as an argument.

- `--headless`: Enable this option to run the scraper in the background without opening a visible Chrome browser window. By default, the scraper opens a visible browser window.

- `--types`: Specify the types of files you want to scrape. This option allows you to filter the file types to be downloaded. Supported file types include JPG, PNG, GIF, and WebM. Specify the types as a comma-separated list.

- `--pause`: Enable this option to introduce a delay (in seconds) between opening each URL and downloading each file. This can be useful to prevent excessive requests to the website. By default, there is no pause between requests.


## Gallery

The script will display the scraped images in a gallery format, allowing you to view and interact with the downloaded images conveniently.

## Disclaimer

Please note that scraping images from websites may violate the terms of service of those websites. Make sure to use this script responsibly and respect the rights of the website owners. The developers of this script are not responsible for any misuse or legal issues arising from the use of this tool.

Happy scraping!
