import requests
import re
import json
from bs4 import BeautifulSoup
from selenium import webdriver 
from os.path import exists
from time import sleep

def get_all_inventory(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    links = []
    boxes = soup.findAll('div', {'class': 'container-2x1-stack'})
    for box in boxes:
        for a in box.findAll('a', {'class': "mb0-5"}, href = True):
            links.append(a['href'])
    links.append('https://www.jellycat.com/us/bags-purses/')
    links.append('https://www.jellycat.com/us/bag-charms/')
    links.append('https://www.jellycat.com/us/backpacks/')
    return links

def get_all_products(url):
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    product_links = []
    for item in soup.findAll('div', {'class': 'listing gproduct relative'}):
        for a in item.findAll('a', {'data-listing': 'name'}, href = True):
            product_links.append('https://www.jellycat.com' + a['href'])
    return product_links

def check_status(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    script = soup.findAll('script', type='text/javascript')[11].text
    raw_json = re.search('variants = ({.*}[ \t\r\n\f]*})', script).group(1).replace("\'", "\"")
    site_json = json.loads(raw_json)
    name = site_json[list(site_json.keys())[0]]['name']
    status = site_json[list(site_json.keys())[0]]['lead_text_summary']
    return (name, status)

if not exists('./product_links.txt'):
    inventory_links = get_all_inventory('https://www.jellycat.com/us/site-map/')
    product_links = []
    for inventory_link in inventory_links:
        print(inventory_link)
        product_links += get_all_products(inventory_link)
    with open('product_links.txt', 'x') as f:
        for link in product_links:
            f.write(link + '\n')

inventory_status = {}
error_items = set()
with open('./product_links.txt', 'r') as f:
    product_links = f.read().splitlines()
    counter, total = 0, len(product_links)
    for link in product_links:
        product_link = link[:-1]
        try:
            name, status = check_status(product_link)
            inventory_status[name] = status
            print(f"Obtained status {counter}/{total}")
            counter += 1
        except:
            print(f"Error occurred with: {product_link}")
            error_items.add(product_link)

csv_str = ''
for key, value in inventory_status.items():
    csv_str += (key + ',' + value + '\n')
csv_str
with open('inventory_status.csv', 'w') as f:
    f.write(csv_str)
