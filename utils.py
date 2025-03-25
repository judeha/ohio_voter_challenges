import re
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  
import json
import os

# Read configs
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

URL_KW = config['url_keywords']

# def is_relevant_text(text: str, keywords: list[str]) -> bool:
#     """Determines if a text is relevant to our search"""
#     for kw in keywords:
#         if text.count(kw) > 0:
#             return True
#     return False

def get_relevant_data(text: str) -> list:
    """Scrapes a text for relevant data"""
    pass

def get_driver():
    """Return a configured chromedriver"""
    # Initialize Chrome options
    chrome_options = webdriver.ChromeOptions()

    # Define print settings to save as PDF
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }

    # Set preferences for Chrome options
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': os.getcwd()  # Set default directory to current working directory
    }

    # Add experimental options and arguments to Chrome options
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # Set up the Chrome WebDriver service and initialize the driver with the specified options
    service = Service("/opt/homebrew/bin/chromedriver")  # Update with your path to chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver