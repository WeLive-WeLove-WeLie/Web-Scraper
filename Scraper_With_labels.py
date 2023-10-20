import requests
from bs4 import BeautifulSoup
import langchain
from langchain.document_transformers import Html2TextTransformer
from langchain.document_loaders import AsyncHtmlLoader
import ssl
from urllib.request import urlopen,Request
from langchain.document_transformers import BeautifulSoupTransformer
import json

base = 'https://www.flipkart.com'

header = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US,en;q=0.9'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

product = 'https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itmdb77f40da6b6d'

req = Request(product, headers=header)
webpage = urlopen(req).read()

soup = BeautifulSoup(webpage, 'html.parser')
html_obj = soup.prettify()
# print(a)
# html_obj = soup.pretiffy()

product_details = {}
product_details['highlights'] = []
product_details['product_description'] = []
for script in soup.find_all('script', attrs={'id': 'jsonLD'}):
    json_data  = json.loads(script.text)
    product_details['rating'] = json_data[0]['aggregateRating']['ratingValue']
    product_details['review_count'] = json_data[0]['aggregateRating']['reviewCount']
    product_details['brand'] = json_data[0]['brand']['name']
    product_details['name'] = json_data[0]['name']
    product_details['image'] = json_data[0]['image']
    product_details['price'] = json_data[0]['offers']['price']
    break
for li in soup.find_all('description', attrs={'class': '_2-riNZ'}):
    product_details['highlights'].append(li.text.strip())

description_headers  = soup.find_all('div', attrs={'class': '_3cFJ8l'})
print(description_headers)
for i,description in enumerate(description_headers):
    print(description)
    product_details['product_description'] = description.text.strip()


with open('product_details.json', 'w') as f:
    json.dump(product_details, f, indent=4,sort_keys=True)

with open('product_details.html', 'w',encoding='utf-8') as f:
    f.write(html_obj)

print('done')










