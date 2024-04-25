from bs4 import BeautifulSoup
import re
from pprint import pprint
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

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

        # Set up the Selenium WebDriver
        self.driver = webdriver.Chrome(
            service=Service(f"{os.getcwd()}/chromedriver.exe")
        )

        self.driver.get(self.site_url)

        # Wait for the page to resolve
        time.sleep(5)

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


def download_images(image_urls):
    for url in image_urls:
        filename = re.search(r"/([\w_-]+[.](jpg|gif|png))$", url)
        if not filename:
            print("Regex didn't match with the url: {}".format(url))
            continue
        with open(filename.group(1), "wb") as f:
            if "http" not in url:
                # sometimes an image source can be relative
                # if it is provide the base url which also happens
                # to be the site variable atm.
                url = "{}{}".format(site, url)
            response = requests.get(url)
            f.write(response.content)


def main():
    scraper = Scraper("zara")
    scraper.scroll_fullpage()
    scraper.get_image_links()


if __name__ == "__main__":
    main()
