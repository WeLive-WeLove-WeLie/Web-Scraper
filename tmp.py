import requests
from bs4 import BeautifulSoup
from langchain.document_transformers import Html2TextTransformer
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
import json

#import HTML2Text

#https://www.flipkart.com/purshottam-wala-women-printed-ethnic-dress-kurta/p/itm1ebc238e2a5a4
base = 'https://www.flipkart.com'

header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }

# product = 'apple-iphone-13-pink-128-gb/p/itm6e30c6ee045d2'
# product = 'apple-iphone-14-plus-blue-128-gb/p/itmac8385391b02b'
product = 'titirangi-4-pack-4wd-monster-truck-cars-push-go-toy-trucks-friction-powered-cars-wheel-drive-vehicles-toddlers-children-boys-girls-kids-gift-4pcs/p/itm5e18b7c4f5a77'

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
        review_pages.append(prod_reviews_url)

    product_details['highlights'] = []
    product_details['product_description'] = []
    for script in soup.find_all('script', attrs={'id': 'jsonLD'}):
        json_data  = json.loads(script.text)
        # print(json_data)
        product_details['rating'] = json_data[0].get('aggregateRating', {}).get('ratingValue', 0)
        product_details['review_count'] = json_data[0].get('aggregateRating', {}).get('reviewCount', 0)
        product_details['brand'] = json_data[0].get('brand', {}).get('name', 0)
        product_details['name'] = json_data[0].get('name', 0)
        product_details['image'] = json_data[0].get('image', 0)
        product_details['price'] = json_data[0].get('offers', {}).get('price', 0)
        break
    
    try:
        for li in soup.find_all('p'):
            # Check for any class, if any reject it
            if li.has_attr('class'):
                continue
            product_details['product_description'].append(li.text.strip())
        product_details['description'] = product_details['product_description'][1]
        product_details['product_description'] = product_details['product_description'][2:-13]
    except:
        pass

    try:
        tmp = soup.find('div',string='Highlights').find_next_sibling()
        # for each text in the highlights, add it to the list
        for li in tmp.find_all('li'):
            product_details['highlights'].append(li.text.strip())
    except:
        pass
    # print(product_details['highlights'])

    #Add specifications
    product_details['specifications'] = {}
    # for li in tmp.find_all('li'):
    #     product_details['specifications'].append(li.text.strip())
    try:
        tmp = soup.find('div',string='Specifications').find_next_sibling().findChild()
        # print(tmp.prettify())
        i = 0
        for cli in tmp:
            li = cli
            curname = li.find('div').text.strip()
            # print(cli.prettify())
            #locate the table
            i = 0
            table = li.find('table')
            table_dict = {}
            for tr in table.find_all('tr'):
                i += 1
                try:
                    table_dict[tr.find('td').text.strip()] = tr.find('td').find_next_sibling().text.strip()
                except:
                    table_dict[curname] = tr.find('td').text.strip()
                    pass
            product_details['specifications'][curname] = table_dict
    except:
        pass
        # break
    # print(product_details['specifications'])
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

def get_reviews(link):
    rev_page = []
    page = requests.get(link, headers=header)
    soup = BeautifulSoup(page.content, 'lxml')
    for li in soup.find_all('div'):
        if li.has_attr('class') and len(li['class']) == 0:
            rev_page.append(li.text.strip())
    rev_page = rev_page[1:-1]
    return rev_page

def main():
    links = get_all_pages(4)[1:]
    get_review_pages(links)
    # return
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
            # if(i == 0):
                # print(docs[i].dict())
    # print(product_details)
    with open('./product/product_details.json', 'w') as f:
        json.dump(product_details, f, indent=4,sort_keys=True)
    print('done')
    #Close the loader
    return

main()