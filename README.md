# ResearchGate Crawler
Python script for crawling ResearchGate.net papers

## About the script
This code start crawling process by urls in ```start.txt``` and give paper details in ```crawled.json```.

## Requirements
First install Python.
Then install these libraries:
```
pip install selenium
pip install webdriver-manager
```

## Parameters
```MAX_FETCH_COUNT```: How many pages you want to crawl?
```MAX_CACHED_NUM```: We renew ```crawled.json``` after crawling each ```MAX_CACHED_NUM``` papers.
