from bs4 import BeautifulSoup

import re
from pprint import pprint

import socket
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

site = "https://www.uniqlo.com/au/en/men/tops/t-shirts"

zara = "https://www.zara.com/au/en/man-tshirts-l855.html?v1=2037185"

# Set up the Selenium WebDriver
driver = webdriver.Chrome(service=Service(f"{os.getcwd()}/chromedriver.exe"))

driver.get(zara)

time.sleep(5)

SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script(f"window.scrollBy(0, 900);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return window.scrollY")
    if new_height == last_height:
        break
    last_height = new_height

page = driver.page_source

soup = BeautifulSoup(page, "html.parser")

img_tags = soup.find_all("img")

img_urls = [img["src"] for img in img_tags]

with open("zara_images.txt", "w+") as file:
    for url in img_urls:
        file.write(f"{url}\n")

# r = requests.get(site, headers=headers)
# html = r.content
# soup = BeautifulSoup(html, "html.parser")

# print(soup.prettify())


# img_tags = soup.find_all("img")
# print(img_tags)
# urls = [img["src"] for img in img_tags]

# for url in urls:
#     filename = re.search(r"/([\w_-]+[.](jpg|gif|png))$", url)
#     if not filename:
#         print("Regex didn't match with the url: {}".format(url))
#         continue
#     with open(filename.group(1), "wb") as f:
#         if "http" not in url:
#             # sometimes an image source can be relative
#             # if it is provide the base url which also happens
#             # to be the site variable atm.
#             url = "{}{}".format(site, url)
#         response = requests.get(url)
#         f.write(response.content)
