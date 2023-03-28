"""
Scrapes blog posts from Medium and writes them to a CSV.
"""
from bs4 import BeautifulSoup
import csv
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

BLOG_URL = 'https://blog.kaporcenter.org/'
FILE_NAME = 'kaporcenter.csv'
COLUMNS = ['published at', 'author', 'title', 'description', 'raw content', 'text content', 'tags']
# Medium uses lazy loading of articles as you scroll down the page.
# This is a simple way to know when to stop scrolling.
LAST_POST_TITLE = 'Ellen Pao and the Myth of Meritocracy'

driver = webdriver.Chrome('chromedriver')

driver.get(BLOG_URL)

print ('loading all articles')
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.implicitly_wait(0.5)
    try:  
      # TODO: update to use the length of articles on the page, if it stops growing then we're at the bottom
      test = driver.find_element(By.XPATH, '//h2[text()="' + LAST_POST_TITLE + '"]')
      print('end of scrolling')
      break
    except NoSuchElementException:
        print('keep scrolling')

articles = driver.find_elements(By.TAG_NAME, 'article')

rows = []

print('scraping posts')

for article in articles:
    href = title.find_element(By.XPATH, './../..').get_attribute("href")
    req = requests.get(href)
    dom = BeautifulSoup(req.text, 'html.parser')
    publishedAt = dom.head.find("meta", { "property": "article:published_time" }).attrs.get("content")
    title = dom.head.find("meta", { "property": "og:title" }).attrs.get("content")
    description = dom.head.find("meta", { "property": "og:description" }).attrs.get("content")
    author = dom.head.find("meta", { "name": "author" }).attrs.get("content")
    content = dom.find("article")
    tags = list(map(lambda tag: tag.text, dom.body.find_all("a", { 'href': re.compile(r'https:\/\/medium\.com\/tag\/') })))

    rows.append([publishedAt, author, title, description, content, content.text, ",".join(tags)])

driver.quit

print('writing csv file')

with open(FILE_NAME, 'w') as csvfile:
    csvwriter = csv.writer(csvfile) 

    csvwriter.writerow(COLUMNS)

    csvwriter.writerows(rows)
