#import dependencies
from bs4 import BeautifulSoup as bs4
import requests
import pymongo
import re
from splinter import Browser
import time
import pandas as pd

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    
    #find Nasa mars news
    browser.visit('https://mars.nasa.gov/news/')
    time.sleep(2)
    soup = bs4(browser.html, 'html.parser')

    news_title = soup.find('div', class_='bottom_gradient').get_text()
    news_p = soup.find('div', class_='rollover_description_inner').get_text()

    #find images of mars
    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    time.sleep(2)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(3)
    browser.click_link_by_partial_text('more info')

    soup = bs4(browser.html, 'html.parser')

    featured_image_path = soup.find('figure', class_='lede').a['href']
    featured_image_url = 'https://www.jpl.nasa.gov' + featured_image_path

    #find mars weather
    browser.visit('https://twitter.com/marswxreport?lang=en')
    time.sleep(2)
    soup = bs4(browser.html, 'html.parser')

    mars_weather = soup.find('div', class_='js-tweet-text-container').get_text()

    #find mars facts
    browser.visit('https://space-facts.com/mars/')
    time.sleep(2)
    soup = bs4(browser.html, 'html.parser')

    mars_table_data = soup.find('table', {'id':"tablepress-mars"})
    mars_data_rows = mars_table_data.find_all('tr')

    row_label = []
    values = []

    for data_row in mars_data_rows:
        td = data_row.find_all('td')
        row_label.append(td[0].text)
        values.append(td[1].text)

    #turn the facts into a dataframe => html table
    mars_facts_df = pd.DataFrame({'Fact': row_label, 'Value': values})
    mars_facts_html_table = mars_facts_df.to_html(header=False, index=False)

    #find info and images about mars hemispheres
    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    time.sleep(2)
    soup = bs4(browser.html, 'html.parser')

    home_link = "https://astrogeology.usgs.gov"

    links = []

    mars_hemispheres = soup.find_all(href=re.compile("search/map/Mars/Viking/"))

    for image in mars_hemispheres:
        hemisphere_url = image.get('href')
        links.append(home_link + hemisphere_url)

    #list(set(links))

    hemis_list = []
    hemis_list = list(set(links))
    hemis_list

    hemisphere_image_urls = []
    hemisphere_names = []
    name_dict = {}

    for link in hemis_list:
        browser.visit(link)
        soup = bs4(browser.html, 'html.parser')
        for big_pic in soup.find_all('a', href=True, text='Original'):
            hemisphere_image_urls.append(big_pic['href'])
            #browser.click_link_by_partial_text('Original')
            hemisphere_name = soup.find_all('h2', class_='title')[0].get_text()
            hemisphere_name_stripped = hemisphere_name.strip('Enhanced')
            hemisphere_name_stripped = hemisphere_name_stripped.rstrip()
            name_dict = {"title": hemisphere_name_stripped, "img_url": big_pic['href']}
            hemisphere_names.append(name_dict.copy())
    
    scraped_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_img": featured_image_url,
        "mars_weather": mars_weather,
        "facts_table": mars_facts_html_table,
        "hemi_names": hemisphere_names
    }


    return scraped_data

