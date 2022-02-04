# this code is written by @SMSadegh19

from lib2to3.pgen2 import driver
import time
import json

from webdriver_manager.chrome import ChromeDriverManager

###### selenium imports
from selenium import webdriver
from selenium.webdriver import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
######

# ids:
crawled_ids = set()
# list of PageDatas:
page_ids = set()
pages_queue = []
MAX_FETCH_COUNT = 2000
MAX_CACHED_NUM = 10
BASE_URL = "https://www.researchgate.net/publication/"
DRIVER_PATH = ChromeDriverManager().install()

cached_pages = []

class PageData:
    def __init__(self, id, url):
        self.url = url
        self.id = id
        self.title = ""
        self.abstract = ""
        self.date = ""
        self.authors = []
        self.references = []
    
    def save_to_json(self):
        global cached_pages
        new_obj = {'id': self.id, 'title': self.title, 'abstract': self.abstract, 'date': self.date, 'authors': self.authors, 'references': self.references}
        cached_pages.append(new_obj)
        if len(cached_pages) > MAX_CACHED_NUM:
            crawled_pages = []
            with open("crawled.json") as f:
                crawled_pages = json.load(f)
                crawled_pages.extend(cached_pages)
                cached_pages = []
            with open("crawled.json", "w") as f:
                json.dump(crawled_pages, f, indent=4)

    def fetch_page(self):
        try:
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
            driver.get(self.url)
            print(self.url)
            time.sleep(3)
            self.url = driver.current_url

            ### get title
            self.title = driver.find_element(By.CSS_SELECTOR, '#lite-page > main > section > section.research-detail-header-section > div > div > h1').text
            print(self.title)

            ### get abstract
            try:
                self.abstract = driver.find_element(By.XPATH, '//*[@id="lite-page"]/main/section/div[1]/div[1]/div/div[2]/div').text
            except:
                self.abstract = ""
            print(self.abstract)

            ### get date
            elem = driver.find_element(By.CSS_SELECTOR, '#lite-page > main > section > section.research-detail-header-section > div > div > div.research-detail-header-section__metadata > div:nth-child(1) > ul > li')
            self.date = elem.text.split()[1]
            print(self.date)

            ### get authors
            # click show all authors
            try:
                elem = driver.find_element(By.XPATH, '//*[@id="lite-page"]/main/section/section[1]/div/div/div[4]/div/span[1]/a')
                if not ("Show" in elem.text):
                    raise ValueError("errrrr")
                elem.click()
            except:
                pass
            # get authors name
            elems = driver.find_elements(By.XPATH, '//*[@id="lite-page"]/main/section/section[1]/div/div/div[3]/div')
            for elem in elems:
                self.authors.append(elem.text.split('\n')[0])
            print(self.authors)

            ### get references
            elems = []
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, '#references > div > div > div > div > div > div > div > div > div > div > div:nth-child(1) > div > a')
                if len(elems) == 0:
                    raise ValueError("errrrrr")
            except:
                elems = driver.find_elements(By.CSS_SELECTOR, '#citations > div > div > div > div > div > div > div > div > div > div > div:nth-child(1) > div > a')
            print(len(elems))
            for elem in elems[:10]:
                ref_url = elem.get_attribute('href')
                self.references.append(get_id_from_url(ref_url))
            print(self.references)

            for ref_id in self.references:
                add_page_to_queue(ref_id)

            self.save_to_json()
            crawled_ids.add(self.id)
        except Exception as err:
            print(err)
            print("Error during fetch:", " id = ", self.id, " url = ", self.url)
        finally:
            driver.quit()


def get_id_from_url(url):
    start = url.index("publication") + 12
    return url[start:].split("_")[0]


def read_crawled_file():
    global crawled_ids, page_ids
    with open("crawled.json") as f:
        crawled_pages = json.load(f)
        for x in crawled_pages:
            page_id, page_references = x['id'], x['references']
            for ref_id in page_references:
                add_page_to_queue(ref_id)
            crawled_ids.add(page_id)
            page_ids.add(page_id)


def read_start_file():
    global pages_queue, page_ids, crawled_ids
    with open("start.txt", "r") as f:
        urls = f.readlines()
        for x in urls:
            url = x.strip()
            pid = get_id_from_url(url)
            add_page_to_queue(pid)


def add_page_to_queue(pid):
    if (pid not in page_ids) and (pid not in crawled_ids):
        pages_queue.append(PageData(pid, BASE_URL + pid))
        page_ids.add(pid)


def get_a_page_to_fetch():
    global pages_queue, crawled_ids
    while len(pages_queue) > 0:
        page = pages_queue.pop()
        if page.id not in crawled_ids:
            return page
    return None


def fetch_pages():
    global crawled_ids
    while len(crawled_ids) < MAX_FETCH_COUNT:
        print("***************** Here we are at crawling ", len(crawled_ids))
        page = get_a_page_to_fetch()
        if page is None:
            print("Queue is empty. There is no more page to crawl. :D")
            break
        page.fetch_page()


read_crawled_file()
read_start_file()

fetch_pages()