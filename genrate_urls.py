import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def read_input_file(input_csv):
    data = pd.read_csv(input_csv, header=None)
    counties = str(data.iloc[0][1])  # Dash separated
    counties = counties.split('-')
    start_search_date = str(data.iloc[1][1]).replace('/', '-')
    end_search_date = str(data.iloc[2][1]).replace('/', '-')

    links_data = []
    for county in counties:
        link_data = {
            'county': county,
            'start_search_date': start_search_date,
            'end_search_date': end_search_date
        }
        links_data.append(link_data)
    return links_data


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def read_instruments_types(input_csv):
    data = pd.read_csv(input_csv)

    instruments = []
    for i, j in data.iterrows():
        if j['Y/N'] == 'Y':
            instruments.append(j['Types'])

    instrument_lists = list(divide_chunks(instruments, 50))

    return instrument_lists


def login():
    username = 'aeldiasty@primerockencap.com'
    password = 'getmein'
    driver.get('https://www.texasfile.com/search/texas/')

    driver.find_element_by_xpath('//*[@id="main-menu"]/div[2]/ul/li[2]/a').click()

    username_input = driver.find_element_by_xpath('//*[@id="loginUsername"]')
    password_input = driver.find_element_by_xpath('//*[@id="loginPassword"]')

    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    username_input.send_keys(username)
    password_input.send_keys(password)
    time.sleep(1)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

    driver.find_element_by_xpath('//*[@id="main-menu"]/div[2]/ul/li[2]/div/div[2]/div/div/div/form/button').click()

    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()


def get_search_url(link_data, instrument_types):
    driver.get(
        'https://www.texasfile.com/search/texas/{}-county/county-clerk-records/'.format(link_data['county'].lower()))

    # time.sleep(4)

    driver.find_element_by_xpath('//*[@id="Form0Name"]').send_keys('*')
    driver.find_element_by_xpath('//*[@id="Form1Name"]').send_keys('*')

    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

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
    instrument_types_search = driver.find_element_by_xpath(
        '//*[@id="react_rendered"]/div/form/div/div[2]/div[1]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div/div/fieldset')
    all_instruments = instrument_types_search.find_elements_by_tag_name("label")
    for label in all_instruments:
        spans = label.find_elements_by_tag_name("span")
        span = spans[0]
        span_text = span.text

        if span_text in instrument_types:
            inputs = label.find_elements_by_tag_name("span")
            input = inputs[0]
            input.click()

    # Press search
    driver.find_element_by_xpath('//*[@id="nameSearchBtn"]').click()

    # time.sleep(3)

    # Get the url
    search_url = driver.current_url
    if 'empty' in search_url:
        search_url = 'No results for this search'
    else:
        search_url = search_url + '?view=table&sorting=-filed_date&page=1'

    return search_url


def add_url_to_output_file(search_url):
    with open('output.txt', 'a') as output_text_file:
        output_text_file.write(search_url + '\n')


def get_last_date_in_last_page(link):
    driver.get(link)

    new_link = link + "00"
    driver.get(new_link)
    last_date = driver.find_element_by_xpath(
        '//*[@id="react_rendered"]/div/form/div/div[2]/div[2]/div[1]/div/div[2]/div/div/div/div[2]/div/table/tbody[50]/tr[1]/td[3]').text
    last_date = last_date.replace('/', '-')
    print('New last Date:', last_date)
    return last_date


def generate_all_urls(links_data, instrument_types):
    new_links_data = []
    for link_data in links_data:
        for instrument_type in instrument_types:
            global driver
            driver = webdriver.Chrome()

            login()
            print('link data', link_data)
            print('instrument types', instrument_type)

            search_url = get_search_url(link_data, instrument_type)
            print("Search URL", search_url)

            add_url_to_output_file(search_url)

            # If the results are in 100 pages!
            number_of_results = driver.find_element_by_xpath(
                '//*[@id="react_rendered"]/div/form/div/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/span[2]').text
            if "5,000" in number_of_results:
                print('This search URL contain 100 pages')
                new_end_search_date = get_last_date_in_last_page(search_url)

                link_data = {
                    'county': link_data['county'],
                    'start_search_date': link_data['start_search_date'],
                    'end_search_date': new_end_search_date
                }
                new_links_data.append(link_data)

            driver.close()
    return new_links_data


if __name__ == "__main__":
    with open('output.txt', 'w') as output_text_file:
        pass

    # Get links Data
    links_data = read_input_file('generate_urls.csv')
    print("Number of Counties:", len(links_data))

    # Get instrument types
    instrument_types = read_instruments_types('instrument_types.csv')

    # Generate all URLs
    while len(links_data) > 0:
        generate_all_urls(links_data, instrument_types)
        links_data = generate_all_urls(links_data, instrument_types)

    print('Done')
