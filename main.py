import requests
from bs4 import BeautifulSoup

HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
                                'Accept-Language': 'en-US, en;q=0.5'})

r = requests.get('https://www.amazon.in/Apple-iPhone-13-128GB-Pink/dp/B09G9FPGTN', headers=HEADERS)
# soup = BeautifulSoup(r.text, 'html.parser')
# print(soup.prettify())
print(r.status_code)
with open('sparx.html', 'w') as f:
    f.write(r.text)
