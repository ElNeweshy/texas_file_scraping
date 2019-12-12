import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def read_input_file(input_csv):
    data = pd.read_csv(input_csv, header=None)
    counties = str(data.iloc[0][1])  # Dash separated
    counties = counties.split('-')
    start_search_date = str(data.iloc[1][1]).replace('/', '-')
    end_search_date = str(data.iloc[2][1]).replace('/', '-')
    types = str(data.iloc[3][1])

    links_data = []
    for county in counties:
        link_data = {
            'county': county,
            'start_search_date': start_search_date,
            'end_search_date': end_search_date,
            'types': types}
        links_data.append(link_data)
    return links_data


def login():
    username = 'aeldiasty@primerockencap.com'
    password = 'getmein'
    driver.get('https://www.texasfile.com/search/texas/')

    driver.find_element_by_xpath('//*[@id="main-menu"]/div[2]/ul/li[2]/a').click()

    username_input = driver.find_element_by_xpath('//*[@id="loginUsername"]')
    password_input = driver.find_element_by_xpath('//*[@id="loginPassword"]')

    username_input.send_keys(username)
    password_input.send_keys(password)
    driver.find_element_by_xpath('//*[@id="main-menu"]/div[2]/ul/li[2]/div/div[2]/div/div/div/form/button').click()


def get_search_url(link_data):
    driver.get(
        'https://www.texasfile.com/search/texas/{}-county/county-clerk-records/'.format(link_data['county'].lower()))

    driver.find_element_by_xpath('//*[@id="Form0Name"]').send_keys('*')
    driver.find_element_by_xpath('//*[@id="Form1Name"]').send_keys('*')

    # Input the dates
    driver.find_element_by_xpath('//*[@id="start_date"]').send_keys(Keys.CONTROL + "a")
    driver.find_element_by_xpath('//*[@id="start_date"]').send_keys(Keys.DELETE)
    driver.find_element_by_xpath('//*[@id="start_date"]').send_keys(link_data['start_search_date'])
    driver.find_element_by_xpath('//*[@id="start_date"]').send_keys(Keys.RETURN)
    driver.find_element_by_xpath('//*[@id="end_date"]').send_keys(Keys.CONTROL + "a")
    driver.find_element_by_xpath('//*[@id="end_date"]').send_keys(Keys.DELETE)
    driver.find_element_by_xpath('//*[@id="end_date"]').send_keys(link_data['end_search_date'])
    driver.find_element_by_xpath('//*[@id="start_date"]').send_keys(Keys.RETURN)


    # Check types
    insturument_types = driver.find_element_by_xpath('//*[@id="react_rendered"]/div/form/div/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div/div/fieldset')
    all_instruments = driver.find_elements_by_tag_name("label")
    for label in all_instruments:
        # input = instrument.find_elements_by_tag_name("input")
        # print(input)
        # input = input[0]
        spans = label.find_elements_by_tag_name("span")
        print(spans)
        # span = spans[0]
        print(span)
        span_text = span.text()
        print(span_text)

    #click Abondoment
    # driver.find_element_by_xpath('//*[@id="react_rendered"]/div/form/div/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div/div/fieldset/label[1]/input').click()

    # Press search
    # driver.find_element_by_xpath('//*[@id="react_rendered"]/div/form/div/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div/div/div/div/div[1]/div[3]/button').click()


    # Get the url
    search_url = driver.current_url
    search_url = search_url + '?view=table&sorting=-filed_date&page=1'

    return search_url


def add_url_to_output_file(search_url):
    with open('output.txt', 'a') as output_text_file:
        output_text_file.write(search_url)


if __name__ == "__main__":
    links_data = read_input_file('generate_urls.csv')
    print("Number of searchs:", len(links_data))

    with open('output.txt', 'w') as output_text_file:
        pass

    global driver
    driver = webdriver.Chrome()

    login()

    for link_data in links_data:
        print(link_data)
        search_url = get_search_url(link_data)
        print("Search URL", search_url)
        add_url_to_output_file(search_url)

    print('Done')
