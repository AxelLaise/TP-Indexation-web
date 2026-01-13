import urllib.request
import urllib.robotparser
import urllib.parse
import time
from bs4 import BeautifulSoup
import json

class Crawler():
    def __init__(self, limit):
        self.base_url = ""                              # The scheme + netloc url for finding robots.txt
        self.robot_parser = None                        # Permissions in robots.txt
        self.limit = limit                              # The limit of pages we want to explore
        self.already_visited = []                       # The pages we already visit to not visit them twice in the same crawling

    def get_html(self, url):
        """
        extract the html code from the given page

        Parameter
        ---------
        url: String
            The url of the page we want to extract the html
        
        Return
        ------
        String
            The html of the page
        """
        request = urllib.request.Request(url=url, method='GET')
        response = urllib.request.urlopen(request)
        data=response.read()
        return(data)
    
    def find_base_url(self, url):
        """
        Parameter
        ---------
        url: String
            The url from where we want to extract the scheme + netloc parts
        
        Return
        ------
        String
            The scheme + netloc parts of the url

        Example
        -------
        >>> crawler = Crawler(limit=50)
        >>> print(crawler.find_base_url('https://web-scraping.dev/products'))
            https://web-scraping.dev
        """
        url_parse = urllib.parse.urlparse(url)
        return url_parse.scheme + "://" + url_parse.netloc

    def read_robots_txt(self):
        """
        Return
        ------
        RobotFileParser
            The object containing all informations about permissions
        """
        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.set_url(self.base_url + "/robots.txt")
        robot_parser.read()
        return robot_parser

    def politeness(self):
        """
        Respect the delay for crawling indicate in the robots.txt or wait 1 second between each parsing to respect politeness
        """
        delay = self.robot_parser.crawl_delay('*')
        if delay is None:
            time.sleep(1)
        else:
            time.sleep(delay)

    def can_parse(self, url):
        """
        Determine if we can parse the page with robots.txt directives

        Parameter
        ---------
        url: String
            The url from the page we want to know if we can parse it
        
        Return
        ------
        bool
            True if we can parse the page and false otherwise
        """
        return self.robot_parser.can_fetch('*', url)
    
    def parse_page(self, url):
        """"
        Parameter
        ---------
        url: String
            The url from the page we want parse
        
        Return
        ------
        BeautifulSoup
            The parse of the page if we can parse it.
        None
            if we can't parse the page
        """
        if self.can_parse(url):
            html = self.get_html(url=url)
            return BeautifulSoup(html, 'html.parser')
        else:
            return None
    
    def extract_title(self, soup):
        """
        Parameter
        ---------
        soup: BeautifulSoup
            The parsing of the htlm page
        Return
        ------
        String
            The title of the page
        """
        return soup.title.contents[0]

    def extract_first_paragraph(self, soup):
        """
        Parameter
        ---------
        soup: BeautifulSoup
            The parsing of the htlm page
        Return
        ------
        String
            The first paragraph of the page if it exist "" otherwise
        """
        first_paragraph = soup.find("p")
        if first_paragraph is None:
            first_paragraph = ""
        else:
            first_paragraph = first_paragraph.contents[0]
        return first_paragraph

    def extract_links(self, soup):
        """
        Parameter
        ---------
        soup: BeautifulSoup
            The parsing of the htlm page
        Return
        ------
        List[String]
            A list of hyperlinks in the page
        """
        links = []
        for link in soup.find_all('a'):
            href = link.get("href")
            if href is None:                    # There is some None links so we remove them to avoid errors
                continue
            if href.startswith("#"):            # There is some links that contains only # so we remove them to avoid errors
                continue
            if not href.startswith("http"):     # Some links do not have the base_url (e.g docs) so we add the base_url before
                href = self.base_url + href
            links.append(href)
        return links

    def extract_one_page(self, url):
        """
        Parameter
        ---------
        url: String
            The page we want to extract informations
        Return
        ------
        Dict()
            A dict wich contains the "url", "title", "description", and "links" of the given page if we can parse it
        None
            if we cannot parse the page
        """
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
    
    def give_priority(self, url):
        """
        Parameter
        ---------
        url: String
            The url of the page we want to know the priority for extraction
        
        Return
        ------
        Integer
            0 if high priority, 1 if medium priority, 2 if weak priority
        """
        if "product/" in url:
            return 0
        elif "products" in url:
            return 1
        else:
            return 2
        

    
    def extract_some_pages(self, url_start):
        """
        The crawling

        Parameter
        ---------
        url_start: String
            The start page of the crawling
        
        Return
        ------
        List[Dict]
            A list where each element is a dict containing informations from one page
        """
        to_visit = []   
        extraction = []
        self.base_url = self.find_base_url(url_start)   # Find the base url to read the robots.txt file
        self.robot_parser = self.read_robots_txt()
        first_page = self.extract_one_page(url_start)
        if first_page is None:                          # If the first page does not exist we return an ampty list
            return extraction
        extraction.append(first_page) 
        self.already_visited.append(url_start)
        for url in extraction[0]["links"]:
                if (self.give_priority(url), url) not in to_visit:
                    to_visit.append((self.give_priority(url), url))     # We add pages to to_visit only if they are not in it to avoid duplication
        nb_of_pages_visited = 1
        while nb_of_pages_visited < self.limit:
            self.politeness()
            to_visit = sorted(to_visit)                 # To put in front pages with high priority
            new_url = to_visit.pop(0)[1]
            new_base_url = self.find_base_url(new_url)
            if new_base_url != self.base_url:           # If we go to another website we have to check the robots.txt of this new site
                self.base_url = new_base_url
                self.robot_parser = self.read_robots_txt()
            page = self.extract_one_page(new_url)
            if page is None:                            # If we cannot parse the page we go to another without incrementing the limit
                continue
            extraction.append(page)
            self.already_visited.append(new_url)
            for url in page["links"]:
                if url not in self.already_visited and (self.give_priority(url),url) not in to_visit:   # Here we also watch if we already visited the page to avoid parsing the same page twice
                    to_visit.append((self.give_priority(url), url))
            nb_of_pages_visited += 1
        extraction = sorted(extraction, key=lambda x: x["url"]) # To sort with the name for better reading
        return extraction

if __name__ == "__main__":
    crawler = Crawler(limit=50)
    extraction = crawler.extract_some_pages("https://web-scraping.dev/products")

    with open('TP1/output_tp1.jsonl', 'w') as file:
        for extract in extraction:
            json.dump(extract, file)
            file.write('\n')