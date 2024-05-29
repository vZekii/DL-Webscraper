from bs4 import BeautifulSoup
import re
from pprint import pprint
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import sys
from urllib.parse import unquote

# Headers to use with the web driver
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# Sites/links to scrape
SITES = {
    "zara_tshirts": "https://www.zara.com/au/en/man-tshirts-l855.html?v1=2037185",
    "uniqlo_tshirts": "https://www.uniqlo.com/au/en/men/tops/t-shirts",
    "iconic_tshirts": "https://www.theiconic.com.au/mens-clothing-tshirts-singlets/",
    "iconic_shirts": "https://www.theiconic.com.au/mens-clothing-shirts-polos/",
    "iconic_coat_jackets_new": "https://www.theiconic.com.au/mens-clothing-coats-jackets/",
    "iconic_sweats_hoods_new": "https://www.theiconic.com.au/mens-clothing-sweats-hoodies/",
    "iconic_jeans_new": "https://www.theiconic.com.au/mens-clothing-jeans/",
    "iconic_pants": "https://www.theiconic.com.au/mens-clothing-pants/",
    "iconic_shorts": "https://www.theiconic.com.au/mens-clothing-shorts/",
    "iconic_womens_skirts": "https://www.theiconic.com.au/womens-clothing-skirts/",
    "iconic_womens_dresses": "https://www.theiconic.com.au/womens-clothing-dresses/",
    "iconic_womens_shorts": "https://www.theiconic.com.au/womens-clothing-shorts/",
    "iconic_womens_tshirts": "https://www.theiconic.com.au/womens-clothing-tshirts-singlets/",
    "iconic_womens_pants": "https://www.theiconic.com.au/womens-clothing-pants/",
    "iconic_womens_sweats_hoods": "https://www.theiconic.com.au/womens-clothing-sweats-hoodies/",
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

    def scroll_multipage(self, num_pages):
        # function to scroll through multiple pages by adding a number in the url, and saving the images from each page while doing so
        for i in range(num_pages):
            self.scroll_fullpage()
            # Get the page source
            page = self.driver.page_source

            # Parse the page source
            soup = BeautifulSoup(page, "html.parser")

            # Find all the image tags
            img_tags = soup.find_all("img")

            # Get the image urls
            img_urls = [img["src"] for img in img_tags if img.has_attr("src")]

            # Save the image urls to a single file, and append the new urls to the file
            last_link = ""
            with open(f"{self.site_name}.txt", "a") as file:
                for url in img_urls:
                    if "static.theiconic.com.au" in url and ":format(webp)" in url:
                        url = remove_webp_extension(url)
                        if last_link != url:
                            file.write(f"{url}\n")
                            last_link = url

            # Scroll to the next page
            self.driver.get(f"{self.site_url}?page={i+2}")
            time.sleep(SCROLL_PAUSE_TIME)

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


def main():
    # for i in list(
    #     [
    #         "iconic_womens_sweats_hoods",
    #         "iconic_womens_pants",
    #         "iconic_womens_shorts",
    #         "iconic_womens_dresses",
    #         "iconic_womens_tshirts",
    #         "iconic_womens_skirts",
    #     ]
    # ):
    scraper = Scraper("iconic_jeans_new")
    scraper.load_site()
    scraper.scroll_multipage(1)
    # scraper.scroll_fullpage()
    # scraper.get_image_links()
    # scraper.download_images_from_file()


def test():
    scraper = Scraper("uniqlo_tshirts")
    scraper.download_images_from_file()


def remove_webp_extension(url):
    decoded_url = unquote(url)  # Decode the URL
    # Check if "/format(webp)" exists in the URL
    if ":format(webp)/" in decoded_url:
        url_split = decoded_url.split(":format(webp)/")
        return url_split[1]

    return url


if __name__ == "__main__":
    main()
