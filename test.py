import requests
from urllib.parse import urlencode, urlparse, urljoin, parse_qs
from urllib.request import Request, urlopen
import json
from bs4 import BeautifulSoup
from utils import get_driver, get_driver_downloader
import time
import yaml
import os
import re
import shutil
import logging
import glob
from langchain_community.document_loaders import PyPDFLoader
import pymupdf4llm

# Read configs
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

BASE_URL = config['base_url']
URL_KW = config['url_keywords']

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# HANDLER
handler = logging.FileHandler('test.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def dev_get_boe_websites():
    # NOTE: 403 Client Error: Forbidden for url
    pass

def dev_get_urls(website, depth, visited=None):
    """Given a website, return list of relevant urls"""
    driver = get_driver()

    # Init visited set
    if visited is None:
        visited = set()
    
    if depth < 0 or website in visited:
        return []

    visited.add(website)
    found_links = []

    # BFS Search
    try:
        # response = requests.get(website, timeout=2)
        driver.get(website)
        response = driver.page_source

        soup = BeautifulSoup(response, "html.parser")

        # Find all links on the page
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(website, a_tag["href"])  # absolute URL
            # Ensure the link is within the same domain to prevent infinite recursion
            if urlparse(link).netloc != urlparse(website).netloc:
                continue
            logger.info(f"{link}")
            if URL_KW.count(link.lower()) > 0:  # check if relevant
                found_links.append(link)
                logger.info(f"FOUND: {link}")

            found_links.extend(dev_get_urls(link, depth - 1, visited))


        time.sleep(1)  # Respectful scraping delay
        driver.quit()

    except requests.RequestException as e:
        print(f"Error fetching {website}: {e}")

    return found_links

    # url = 'https://www.brides.com/story/how-to-write-the-perfect-best-man-speech'
    # https://www.google.com/search?q=StackOverflow
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, features="html.parser")
    # for tag in soup.find_all('h3'):
    #     print(tag.text.strip())
    
def is_relevant_log_entry(log_entry, keywords):
    """Given a log entry, determine if it is relevant"""
   # read log entry of format 2025-03-27 16:47:10,942 - __main__ - INFO - https://www.boe.ohio.gov/fayette/voter-registration-information/how-to-register/
    url = log_entry.split(' - ')[-1]
    return (any(kw in url for kw in keywords))

def get_relevant_urls(log_file, keywords):
    """Given a path to a log file, returns list of relevant urls"""
    with open(log_file, 'r') as f:
        log_entries = f.readlines()

    relevant_urls = []
    for log_entry in log_entries:
        if is_relevant_log_entry(log_entry, keywords):
            relevant_urls.append(log_entry.split(' - ')[-1])
    
    return relevant_urls

def dev_get_meeting_minutes(url):
    """Given a URL, return list of all to meeting minutes"""
    driver = get_driver()
    driver.get(url)
    response = driver.page_source
    soup = BeautifulSoup(response, "html.parser")

    minutes_url = []
    # Find all meeting minutes on the page
    for a_tag in soup.find_all("a", href=True):
        # if is pdf or contains 'minutes'
        if a_tag["href"].endswith(".pdf") or "minutes" in a_tag["href"].lower():
            minutes_url.append(a_tag["href"])
    return minutes_url

def dev_download_meeting_minutes(url):
    """Given a URL, download the meeting minutes to a pdf in 'data/' """
    driver = get_driver_downloader()
    driver.get(url)

    return

def dev_ocr(pdf_path, save_path):
    """Given a path to a saved pdf, convert to txt with ocr"""

    # Get Langchain Document with OCR
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    # Get plaintext to save to new file
    with open(save_path, 'w') as f:
        for page in pages:
            f.write(page.page_content)
            f.write("\n\n")

    return

def dev_find_challenges(txt_path):
    # print lines that contain keywords
    relevant_lines = []
    with open(txt_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if URL_KW.count(line.lower()) > 0:
                relevant_lines.append(line)
    return relevant_lines

if __name__ == "__main__":
    # Get pdf paths
    for pdf_path in glob.glob("data/pdf/*.pdf"):
        # strip .pdf
        save_path = "data/txt/" + pdf_path[9:-4] + ".txt"
        pages = dev_ocr(pdf_path, save_path)