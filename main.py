import requests

r = requests.get('https://www.amazon.in/Sparx-Mens-Sneaker-White-Black/dp/B0B4KCH1LV/ref=lp_90767607031_1_1')
with open('sparx.html', 'w') as f:
    f.write(r.text)