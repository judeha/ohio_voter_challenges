import requests
from urllib.parse import urlencode, urlparse, urljoin, parse_qs
from urllib.request import Request, urlopen
import json
from bs4 import BeautifulSoup
from utils import get_driver
import time
import yaml
import logging

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
    """Given a website, search for relevant urls"""
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

def test_chrome():
    url = "https://www.brides.com/story/how-to-write-the-perfect-best"
    driver = get_driver()
    driver.get(url)

if __name__ == "__main__":
    # read json
    with open('boe_websites.json') as f:
        counties = json.load(f)
    
    for c,url in counties.items():
        try:
            dev_get_urls(url, 2)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")