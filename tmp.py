import requests
from bs4 import BeautifulSoup
from langchain.document_transformers import Html2TextTransformer
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
import json

#import HTML2Text


base = 'https://www.flipkart.com'

header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }

product = 'apple-iphone-13-pink-128-gb/p/itm6e30c6ee045d2'
# product = 'apple-iphone-14-plus-blue-128-gb/p/itmac8385391b02b'

product_details = {}
reviews = []

def get_reviews_url(soup): 
    test = soup.find_all('a', href=lambda value: value and 'product-reviews' in value)
    return test[-1]['href']


def get_all_pages(num_pages):
    # Goto the product page and get the HTML content of the page
    url = f'{base}/{product}'
    main_page = requests.get(url, headers=header)
    # bs_transformer = Html2TextTransformer()
    print("initial page status code: ", main_page.status_code)

    # with open('spar.html', 'w', encoding="utf-8") as f:
    #     f.write(page.text)
    soup = BeautifulSoup(main_page.content, 'lxml')
    
    # Get the product reviews page url and get the HTML content of the page
    tmp = get_reviews_url(soup)
    review_pages = []
    review_pages.append(url)
    for i in range(0, num_pages):
        prod_reviews_url = f'{base}{tmp}&page={i+1}'
        # prod_reviews_page = requests.get(prod_reviews_url, headers=header)
        # Print the status code of the page
        # tmp = prod_reviews_page.content
        # tmp = bs_transformer.transform_documents(tmp)
        review_pages.append(prod_reviews_url)

    product_details['highlights'] = []
    product_details['product_description'] = []
    for script in soup.find_all('script', attrs={'id': 'jsonLD'}):
        json_data  = json.loads(script.text)
        # print(json_data)
        product_details['rating'] = json_data[0]['aggregateRating']['ratingValue']
        product_details['review_count'] = json_data[0]['aggregateRating']['reviewCount']
        product_details['brand'] = json_data[0]['brand']['name']
        product_details['name'] = json_data[0]['name']
        product_details['image'] = json_data[0]['image']
        product_details['price'] = json_data[0]['offers']['price']
        break
    for li in soup.find_all('p'):
        # Check for any class, if any reject it
        if li.has_attr('class'):
            continue
        product_details['product_description'].append(li.text.strip())
    product_details['product_description'] = product_details['product_description'][:-13]
    # product_details['highlights'] = product_details['product_description'][2:]
    product_details['description'] = product_details['product_description'][1]
    return review_pages

def get_review_pages(links):
    for link in links:
        rev_page = []
        page = requests.get(link, headers=header)
        soup = BeautifulSoup(page.content, 'lxml')
        for li in soup.find_all('div'):
            if li.has_attr('class') and len(li['class']) == 0:
                rev_page.append(li.text.strip())
        rev_page = rev_page[1:-1]
        reviews.append(rev_page)
    return

def main():
    links = get_all_pages(4)[1:]
    get_review_pages(links)
    loader = AsyncHtmlLoader(links, header)
    docs = loader.load()
    print('loaded')
    html2text = Html2TextTransformer()
    # soup_transformer = BeautifulSoupTransformer()
    
    docs = html2text.transform_documents(docs)
    for i in range(0, len(links)):
        with open(f'./product/reviews/page{i+1}.txt', 'w', encoding="utf-8") as f:
            for line in reviews[i]:
                f.write(line)
                f.write('\n')
    for i in range(0, len(links)):
        with open(f'./product/langchain_rev/page{i+1}.txt', 'w', encoding="utf-8") as f:
            f.write(docs[i].page_content)
            if(i == 0):
                print(docs[i].dict())
    # print(product_details)
    with open('./product/product_details.json', 'w') as f:
        json.dump(product_details, f, indent=4,sort_keys=True)
    print('done')
    #Close the loader
    return

main()