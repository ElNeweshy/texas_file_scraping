import time
import re
from copy import deepcopy
import ast
import os

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

username = 'aeldiasty@primerockencap.com'
password = 'getmein'


def get_urls(text_file):
    urls = open(text_file, 'r').readlines()

    for i, url in enumerate(urls):
        if '&page=' not in url:
            url = url + '&page==1'
            urls[i] = url
    return urls


def get_data(url, text_file_name):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)

    username_input = driver.find_element_by_xpath('//*[@id="id_username"]')
    password_input = driver.find_element_by_xpath('//*[@id="id_password"]')

    username_input.send_keys(username)
    password_input.send_keys(password)

    # submit
    driver.find_element_by_xpath('//*[@id="submit"]').click()

    # Git the number of results
    # number_of_results = BeautifulSoup(driver), 'html.parser').find('span').text
    number_of_results = driver.find_element_by_xpath(
        '//*[@id="react_rendered"]/div/form/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[4]/span/strong').text
    number_of_pages = int(eval(number_of_results) / 50) + 1
    if eval(number_of_results) / 50 == int(eval(number_of_results) / 50):
        number_of_pages = int(eval(number_of_results) / 50)

    # Create text file
    with open(text_file_name, 'w') as ouput_text_file:
        pass

    # parse
    counter = 1
    while counter <= number_of_pages:  # number_of_pages
        cut_from_link = re.findall('=\d+$', url)[0]
        total_length = len(url) - len(cut_from_link)
        desired_link = url[:total_length] + '=' + str(counter)

        print(desired_link)
        driver.get(desired_link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find_all('tbody')  # , attrs={'class':'class="BlackText VertAlignTop"'}

        dicts = []
        for row in rows:
            dict = {'type': '',
                    'date_field': '',
                    'third_column_data_number': '',
                    'third_column_data_bk': '',
                    'third_column_data_volpg': '',
                    'grantor': '',
                    'grantee': '',
                    'survey_name': '',
                    'section': '',
                    'block': '',
                    'acreage': '',
                    'abstract': '',
                    'number': '',
                    'town_ship': '',
                    }
            parse_row = BeautifulSoup(str(row), 'html.parser')
            tds = parse_row.find_all('td')

            # 1
            type = BeautifulSoup(str(tds[1]), 'html.parser').find('span').text
            dict.update({'type': type})

            # 2
            date_field = BeautifulSoup(str(tds[2]), 'html.parser').find('td').text
            dict.update({'date_field': date_field})

            # 3, 4, 5
            third_column_data = BeautifulSoup(str(tds[3]), 'html.parser').find('td').text

            try:
                third_column_data = third_column_data.replace("| ", '')
            except:
                pass

            if 'N/A' in third_column_data:
                splitter = 'N/A'
            else:
                splitter = re.findall(r'[A-Z]+', third_column_data)

            try:
                third_column_data_number = third_column_data.split(splitter[0])[0].strip()
                third_column_data_bk = splitter[0]
                third_column_data_volpg = third_column_data.split(splitter[0])[1].strip()
            except:
                third_column_data_number = third_column_data[:5]
                third_column_data_bk = third_column_data[5:10]
                third_column_data_volpg = third_column_data[10:]

            dict.update({'third_column_data_number': third_column_data_number})
            dict.update({'third_column_data_bk': third_column_data_bk})
            dict.update({'third_column_data_volpg': third_column_data_volpg})


            # 6
            grantors = BeautifulSoup(str(tds[4]), 'html.parser').find_all('li')

            for i, grantor in enumerate(grantors):
                grantor = BeautifulSoup(str(grantor), 'html.parser').find('li').text
                grantors[i] = grantor

            if len(grantors) > 1:
                grantor = ' - '.join(grantors)
            else:
                grantor = grantors[0]
            dict.update({'grantor': grantor})

            # 7
            # grantee = BeautifulSoup(str(tds[5]), 'html.parser').find('li').text
            # dict.update({'grantee': grantee})

            grantees = BeautifulSoup(str(tds[5]), 'html.parser').find_all('li')

            for i, grantee in enumerate(grantees):
                grantee = BeautifulSoup(str(grantee), 'html.parser').find('li').text
                grantees[i] = grantee

            if len(grantees) > 1:
                grantee = ' - '.join(grantees)
            else:
                grantee = grantees[0]
            dict.update({'grantee': grantee})



            # 8, 9, 10, 11, 12, 13, 14
            legal_description = BeautifulSoup(str(tds[6]), 'html.parser').find_all('li')
            last_part_dictionary = {
                'Survey Name': 'survey_name',
                'Section': 'section',
                'Block': 'block',
                'Acreage': 'acreage',
                'Abstract ': 'abstract',
                'Number': 'number',
                'Township': 'town_ship',
            }

            for item in legal_description:
                content = BeautifulSoup(str(item), 'html.parser').find('li').text
                content1, content2 = content.split(':')

                try:
                    content1 = last_part_dictionary[content1]
                    content2 = content2.strip()
                    dict.update({content1: content2})
                except:
                    continue

            # Save data
            with open(text_file_name, 'a') as ouput_text_file:
                ouput_text_file.write(str(dict))
                ouput_text_file.write('\n')

            dicts.append(deepcopy(dict))
        counter += 1

    return dicts

def create_csv_form_text_file(text_file, output_file_name):
    columns = ['type',
               'date_field',
               'third_column_data_number',
               'third_column_data_bk',
               'third_column_data_volpg',
               'grantor',
               'grantee',
               'survey_name',
               'section',
               'block',
               'acreage',
               'abstract',
               'number',
               'town_ship'
               ]

    dicts = open(text_file, 'r').readlines()

    df = pd.DataFrame(columns=columns)
    for dict in dicts:
        dict = ast.literal_eval(dict)
        df = df.append(dict, ignore_index=True)

    df.index = np.arange(1, len(df) + 1)
    df.to_csv(output_file_name)


if __name__ == '__main__':
    version = '1.2'
    print('Initializing texas_file_scrap version {}'.format(version), '\n')

    links_file = 'links.csv'

    df = pd.read_csv(links_file, header=None)
    number_of_rows = df.shape[0]

    print('Working on {} URLs'.format(number_of_rows))

    for index, row in df.iterrows():
        # Get data from SCV
        file_name = row[0]
        url = row[1]
        if '&page=' not in url:
            url = url + '&page=1'

        print('Working on {}'.format(url))

        # File names
        text_file_name = '{}.txt'.format(file_name)
        csv_file_name = '{}.csv'.format(file_name)

        # Scrap
        data = get_data(url, text_file_name)
        create_csv_form_text_file(text_file_name, csv_file_name)
        os.remove(text_file_name)

        print('{} has been generated successfully.'.format(csv_file_name))

    print('The process is done')