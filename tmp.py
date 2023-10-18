import requests
from bs4 import BeautifulSoup
from langchain.document_transformers import Html2TextTransformer
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
#import HTML2Text


base = 'https://www.flipkart.com'

header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }

product = 'apple-iphone-13-pink-128-gb/p/itm6e30c6ee045d2'

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
    
    return review_pages
    
    for i in range(0, 2):
        with open(f'page{i+1}.txt', 'w', encoding="utf-8") as f:
            f.write(review_pages[i].page_content)
    
    return review_pages

def main():
    links = get_all_pages(2)
    loader = AsyncHtmlLoader(links, header)
    docs = loader.load()
    print('loaded')
    html2text = Html2TextTransformer()
    # soup_transformer = BeautifulSoupTransformer()
    docs = html2text.transform_documents(docs)
    for i in range(0, len(links)):
        with open(f'page{i+1}.txt', 'w', encoding="utf-8") as f:
            f.write(docs[i].page_content)
    print('done')
    return

main()