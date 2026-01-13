import urllib.request
import urllib.robotparser
import urllib.parse
import time
from bs4 import BeautifulSoup
import json

class Crawler():
    def __init__(self, limit):
        self.base_url = ""
        self.rp = self.read_robots_txt()
        self.limit = limit
        self.already_visited = []

    def get_html(self, url):
        request = urllib.request.Request(url=url, method='GET')
        response = urllib.request.urlopen(request)
        data=response.read()
        return(data)
    
    def find_base_url(self, url):
        url_parse = urllib.parse.urlparse(url)
        return url_parse.scheme + "://" + url_parse.netloc

    def read_robots_txt(self):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(self.base_url + "/robots.txt")
        rp.read()
        return rp

    def politeness(self):
        delay = self.rp.crawl_delay('*')
        if delay is None:
            time.sleep(1)
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

    def extract_one_page(self, url):
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

            return extraction
    
    def give_priority(self, link):
        if "product/" in link:
            return 0
        elif "products" in link:
            return 1
        else:
            return 2
        

    
    def extract_some_pages(self, url_dep):
        to_visit = []
        extraction = []
        self.base_url = self.find_base_url(url_dep)
        extraction.append(self.extract_one_page(url_dep))
        self.already_visited.append(url_dep)
        for link in extraction[0]["links"]:
                if (self.give_priority(link), link) not in to_visit:
                    to_visit.append((self.give_priority(link), link))
        nb_of_pages_visited = 1
        while nb_of_pages_visited < self.limit:
            self.politeness()
            to_visit.sort()
            new_base_url = self.find_base_url(to_visit[0][1])
            if new_base_url != self.base_url:
                self.base_url = new_base_url
                self.rp = self.read_robots_txt()
            extraction.append(self.extract_one_page(to_visit[0][1]))
            self.already_visited.append(to_visit.pop(0)[1])
            for link in extraction[nb_of_pages_visited]["links"]:
                if link not in self.already_visited and (self.give_priority(link),link) not in to_visit:
                    to_visit.append((self.give_priority(link), link))
            nb_of_pages_visited += 1
        return extraction

if __name__ == "__main__":
    crawler = Crawler(base_url="https://web-scraping.dev", limit=50)
    extraction = crawler.extract_some_pages("https://web-scraping.dev/products")

    with open('TP1/output_tp1', 'w') as fichier:
        for extract in extraction:
            json.dump(extract, fichier)
            fichier.write('\n')