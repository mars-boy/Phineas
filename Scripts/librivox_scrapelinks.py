import os
import os.path as path
import scipy
import requests
import numpy as np
import html5lib
from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
import pathlib
import urllib.request

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpoCon
from selenium.webdriver.common.by import By

pagination_range_to_scrape = 35
driver = webdriver.Chrome()

MB = 'MB'
EMPTY_STR = ''
librivox_file_name = 'librivox_download_links.txt'
NEW_LINE = '\n'
CURRENT_DIRECTORY = os.getcwd()

timeout = 4 

book_div_list = []
book_download_list = []

for i in range(pagination_range_to_scrape):
    url = (
        """https://librivox.org/search?title=&author=&reader=&keywords=&genre_id=0
        &status=complete&project_type=solo&recorded_language=english&sort_order=catalog_date
        &search_page={}&search_form=advanced""").format(i)
    driver.get(url)
    book_divs = WebDriverWait(driver,timeout*1000).until(ExpoCon.presence_of_element_located((By.CLASS_NAME, "catalog-result")))
    pagedata = driver.page_source
    soup = BeautifulSoup(pagedata,'html.parser')
    book_list_li = soup.find_all('li', class_='catalog-result')
    for book in book_list_li:
        download_size = float(book.find('div', class_='download-btn').span.text.replace(MB,EMPTY_STR))
        if(download_size < 100):
            download_url = book.h3.a.get('href')
            if not download_url in book_download_list:
                book_download_list.append(download_url)

mode = os.O_CREAT

if not os.path.exists(librivox_file_name):
    lib_file = os.open(librivox_file_name, mode)
    os.close(lib_file)


existing_links = [line.strip(NEW_LINE) for line in open(librivox_file_name, 'r')]
book_download_list = [item for item in book_download_list if item not in existing_links]

with open(librivox_file_name, 'a') as librivox_file:
    librivox_file.write(NEW_LINE.join(book_download_list))

# Download links
# Today I'm lazy to write a separate file so I'll move the code later on 
# until then let it rest here

books_main_links_list = [line.strip(NEW_LINE) for line in open(librivox_file_name, 'r')]
for url in books_main_links_list:
    driver.get(url)
    temp = WebDriverWait(driver,timeout*1000).until(ExpoCon.presence_of_element_located((By.CLASS_NAME, "book-download-btn")))
    pagedata = driver.page_source
    soup = BeautifulSoup(pagedata,'html.parser')
    read_by = soup.select('dl.product-details dd a')[0].text
    file_directory = os.path.join(CURRENT_DIRECTORY, 'Speakers', read_by)
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
    download_link = soup.select('dl.listen-download dd a')[0].get('href')
    final_directory = os.path.join(file_directory, download_link.split("http://www.archive.org/download//")[1].replace(r'/','_'))
    if not os.path.exists(final_directory):
        urllib.request.urlretrieve(download_link, final_directory)