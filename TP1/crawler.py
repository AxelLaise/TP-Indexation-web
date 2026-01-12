import urllib.request
import urllib.robotparser
import time
from bs4 import BeautifulSoup

class Crawler():
    def get_html(self, url):
        request = urllib.request.Request(url=url, method='GET')
        response = urllib.request.urlopen(request)
        data=response.read()
        return(data)

    def get_robots_txt(self, base_url):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(base_url + "/robots.txt")
        rp.read()
        self.base_url = base_url
        self.rp = rp

    def politeness(self):
        delay = self.rp.crawl_delay('*')
        if delay is None:
            time.sleep(0.5)
        else:
            time.sleep(delay)

    def can_parse(self, url):
        return self.rp.can_fetch('*', url)
    
    def parse_page(self, url):
        if self.can_parse(url):
            html = self.get_html(url=url)
            return BeautifulSoup(html, 'html.parser')
        else:
            return None
    
    def extract_title(self, soup):
        return soup.title.contents[0]

    def extract_first_paragraph(self, soup):
        first_paragraph = soup.find("p")
        if first_paragraph is None:
            first_paragraph = ""
        else:
            first_paragraph = first_paragraph.contents[0]
        return first_paragraph

    def extract_links(self, soup):
        links = []
        for link in soup.find_all('a'):
            href = link.get("href")
            if href is None:
                continue
            if href.startswith("#"):
                continue
            if not href.startswith("http"):
                href = self.base_url + href
            links.append(href)
        return links

    def extract(self, url):
        soup = self.parse_page(url)
        if soup is None:
            return None
        else:
            title = self.extract_title(soup)
            first_paragraph = self.extract_first_paragraph(soup)
            links = self.extract_links(soup)
            extraction = {}
            extraction["url"] = url
            extraction["title"] = title
            extraction["description"] = first_paragraph
            extraction["links"] = links
            print(links)
            return extraction

    

crawler = Crawler()
crawler.get_robots_txt(base_url="https://web-scraping.dev")
crawler.extract("https://web-scraping.dev/products")