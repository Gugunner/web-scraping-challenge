# Dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd
import re
import time
import pymongo




# urls to scrape
mars_news_url = 'https://mars.nasa.gov/news/'
mars_images_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
mars_weather_url = 'https://twitter.com/marswxreport?lang=en'
mars_facts_url = 'https://space-facts.com/mars/'
mars_hemipsheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
# NASA MARS NEWS
def scrape_mars_news(browser):
    mars_news = {}
    browser.visit(mars_news_url)
    time.sleep(5)
    titles_list = []
    articles_list = []
    for x in range(1, 4):
        html = browser.html
        soup = bs(html, 'lxml')
        articles = soup.find_all('li', class_='slide')
        for z in articles:
            titles_list.append(z.find('h3').text.strip())
            articles_list.append(z.find('div', class_='article_teaser_body').text.strip())
        try:
            links_found = browser.links.find_by_text('More').click()
        except:
            print(f'No page {x + 1}')
    return {
            'Titles': titles_list,
            'Articles': articles_list
    }
#JPL MARS SPACE IMAGES - FEATURED IMAGE
def  scrape_mars_featured_image(browser):
    browser.visit(mars_images_url)
    image_url = ''
    try:
        browser.find_by_id('full_image').click()
        time.sleep(5)
        html = browser.html
        soup = bs(html, 'lxml')
        image_url = soup.find('img', class_='fancybox-image')
    except:
        print('Could not get full image')
    image_url = f'https://www.jpl.nasa.gov{image_url["src"]}'
    return image_url

#MARS WEATHER
def scrape_mars_weather(browser):
    browser.visit(mars_weather_url)
    time.sleep(5)
    html = browser.html
    soup = bs(html, 'lxml')
    mars_weather = (
        soup.
            find('article', class_='css-1dbjc4n r-1loqt21 r-18u37iz r-1ny4l3l r-o7ynqc r-6416eg').
            find_all('span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")[4].
            text.
            strip()
    )
    mars_weather_found = re.search("low .+ high .+ºF\)", mars_weather)
    mars_weather = mars_weather_found[0] if mars_weather_found else 'no weather found'
    mars_weather = re.sub("ºF", " Farenheit", mars_weather)
    mars_weather = re.sub("ºC", " Celsius", mars_weather)
    return mars_weather
#MARS FACTS
def scrape_mars_facts():
    mars_facts_table = pd.read_html(mars_facts_url)
    mars_facts_table_df = mars_facts_table[0]
    mars_facts_table_df.columns = ['Property', 'Measures']
    mars_facts_table_df.to_html('table.html', index=False)

#MARS HEMISPHERES
def scrape_mars_hemishperes(browser):
    browser.visit(mars_hemipsheres_url)
    mars_images_dict = []
    idx = -1;
    for _ in browser.find_by_css(".description"):
        try:
            img = browser.find_by_css(".description")
            idx += 1
            link = img[idx].find_by_css(".itemLink").first
            title = link.text
            link.click()
            url = browser.find_by_text(' (jpg) 1024px wide').first
            href = bs(url.html, 'lxml').find('a')['href']
            print(title)
            mars_images_dict.append({"title": title, "img_url": href})
            browser.back()
            time.sleep(0.5)
        except:
            print('Anchor not found')
    return mars_images_dict

def scrape():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    mars_news = scrape_mars_news(browser)
    featured_image = scrape_mars_featured_image(browser)
    mars_weather = scrape_mars_weather(browser)
    mars_hemispheres = scrape_mars_hemishperes(browser)
    mars = {
        "mars_news": mars_news,
        "mars_featured_image": featured_image,
        "mars_weather": mars_weather,
        "mars_hemispheres": mars_hemispheres
    }
    return mars

