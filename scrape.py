from bs4 import BeautifulSoup
import re
from pprint import pprint
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import sys

# Headers to use with the web driver
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# Sites/links to scrape
SITES = {
    "zara_tshirts": "https://www.zara.com/au/en/man-tshirts-l855.html?v1=2037185",
    "uniqlo_tshirts": "https://www.uniqlo.com/au/en/men/tops/t-shirts",
}

# Change depending on how long the page takes to load - wifi dependent
SCROLL_PAUSE_TIME = 1


class Scraper:

    def __init__(self, site):
        self.site_name = site
        self.site_url = SITES[site]

        self.driver_location = ""
        # Set up the Selenium WebDriver
        if sys.platform.startswith("win32"):
            self.driver_location = f"{os.getcwd()}/chromedriver.exe"
        elif sys.platform.startswith("darwin"):
            self.driver_location = f"{os.getcwd()}/chromedriver"
        else:
            raise Exception("Platform not detected or incorrect")

    def load_site(self, time_to_wait=5):
        if not os.path.isfile(self.driver_location):
            raise Exception(
                "You'll need to install chromedriver, check the readme for downloads"
            )
        self.driver = webdriver.Chrome(service=Service(self.driver_location))

        self.driver.get(self.site_url)

        # Wait for the page to resolve
        time.sleep(time_to_wait)

    def scroll_fullpage(self):
        """Function to scroll the page fully slowly to load all the images"""

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down by a bit
            self.driver.execute_script(f"window.scrollBy(0, 900);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return window.scrollY")
            if new_height == last_height:
                break
            last_height = new_height
        return

    def get_image_links(self):
        page = self.driver.page_source

        soup = BeautifulSoup(page, "html.parser")

        img_tags = soup.find_all("img")

        img_urls = [img["src"] for img in img_tags]

        with open(f"{self.site_name}.txt", "w+") as file:
            for url in img_urls:
                file.write(f"{url}\n")

        return img_urls

    def download_images_from_file(self):
        # Check if the file exists before opening it
        if not os.path.isfile(f"{self.site_name}.txt"):
            print("File not found, please run get_image_links first")
            return

        with open(f"{self.site_name}.txt", "r") as file:
            urls = file.readlines()

        # Show how many are going to be downloaded
        print(f"Downloading {len(urls)} images from {self.site_name}")

        # Download all the images from the urls in the file
        for i, url in enumerate(urls):
            response = requests.get(url.strip(), headers=HEADERS)
            if not os.path.exists(self.site_name):
                os.makedirs(self.site_name)
            with open(f"{self.site_name}/{i}.jpg", "wb") as image:
                image.write(response.content)

            break


def main():
    scraper = Scraper("zara_tshirts")
    scraper.load_site()
    scraper.scroll_fullpage()
    scraper.get_image_links()
    scraper.download_images_from_file()


def test():
    scraper = Scraper("zara_tshirts")
    scraper.download_images_from_file()


if __name__ == "__main__":
    test()
