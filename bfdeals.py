from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import argparse

#Comment out these 3 lines and change the searchterm variable, if you do not wish to use argparse version
my_parser = argparse.ArgumentParser(description='Return BF Amazon Deals')
my_parser.add_argument('searchterm', metavar='searchterm', type=str, help='The item to be searched for. Use + for spaces')
args = my_parser.parse_args()

searchterm = args.searchterm

s = HTMLSession()
dealslist = []


url = f'https://www.amazon.co.uk/s?k={searchterm}&i=black-friday'

def getdata(url):
    r = s.get(url)
    r.html.render(sleep=1)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    return soup

def getdeals(soup):
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    for item in products:
        title = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.strip()
        short_title = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.strip()[:25]
        link = item.find('a', {'class': 'a-link-normal a-text-normal'})['href']
        try:
            saleprice = float(item.find_all('span', {'class': 'a-offscreen'})[0].text.replace('£','').replace(',','').strip())
            oldprice = float(item.find_all('span', {'class': 'a-offscreen'})[1].text.replace('£','').replace(',','').strip())
        except:
            oldprice = float(item.find('span', {'class': 'a-offscreen'}).text.replace('£','').replace(',','').strip())
        try:
            reviews = float(item.find('span', {'class': 'a-size-base'}).text.strip())
        except:
            reviews = 0

        saleitem = {
            'title': title,
            'short_title': short_title,
            'link': link,
            'saleprice': saleprice,
            'oldprice': oldprice,
            'reviews': reviews            
            }
        dealslist.append(saleitem)
    return

def getnextpage(soup): 
    pages = soup.find('ul', {'class': 'a-pagination'})   
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = 'https://www.amazon.co.uk' + str(pages.find('li', {'class': 'a-last'}).find('a')['href'])
        return url
    else:
        return

while True:
    soup = getdata(url)
    getdeals(soup)
    url = getnextpage(soup)
    if not url:
        break
    else:
        print(url)
        print(len(dealslist))  


df = pd.DataFrame(dealslist)
df['percentoff'] = 100 - ((df.saleprice / df.oldprice) * 100)
df = df.sort_values(by=['percentoff'], ascending=False)
df.to_csv(searchterm + '-bfdeals.csv', index=False)
print('Fin.')
