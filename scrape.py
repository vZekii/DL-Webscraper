from bs4 import BeautifulSoup
import urllib
import requests
import re
from pprint import pprint


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

site = "https://www.uniqlo.com/au/en/men/tops/t-shirts"
r = requests.get(site, headers=headers)
html = r.content
soup = BeautifulSoup(html, "html.parser")

print(soup.prettify())


img_tags = soup.find_all("img")
print(img_tags)
urls = [img["src"] for img in img_tags]

for url in urls:
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
