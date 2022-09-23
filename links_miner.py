from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep, time
from bs4 import BeautifulSoup
import requests
import csv
import re
import os
import glob

def get_links():
    links = []
    with open('groups.txt', 'r') as f:
        for line in f:
            links.append(line.rstrip('\n'))

    return links

valid_links = get_links()

def is_exist(username, count):
    url = 'https://t.me/' + username

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        members = soup.find('div', {'class': 'tgme_page_extra'})
        if members:
            m = members.text.replace(" ", '')
            m = m.split(',')

            if m[0].endswith('members'):
                n = re.split('(\d+)', str(m[0]))
                # print(username, int(n[1]))

                if username not in valid_links and 'https://t.me/' + username not in valid_links:
                    with open('output.csv', 'a', encoding='utf-8', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([
                            username, int(n[1])
                        ])

                    with open(f'data/groups_{count}.txt', 'a+') as f:
                        f.write(username + '\n')

                    valid_links.append(username)

                    print('[+]', username)
    except:
        pass

def work_with_group(driver, link, count):
    # time to scroll one group in seconds
    TIME_SCROLL_SECONDS = 600

    try:
        t0 = time()

        print(f'-- Working with {link} -- ')

        if 'http' in link:
            driver.get('https://web.telegram.org/k/#@' + link.split('/')[-1])

        elif '@' in link:
            driver.get('https://web.telegram.org/k/#' + link)

        else:
            driver.get('https://web.telegram.org/k/#@' + link)

        sleep(5)

        driver.find_element(By.XPATH, "//div[@class='tabs-tab main-column']").click()

        urls = []
        while True:

            elements = driver.find_elements(By.XPATH, "//div[@class='bubbles-group']")

            for element in elements:
                try:
                    for el in re.findall(
                            'http[s]?://t.me(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                            element.text):
                        if '<' in el:
                            urls.append(el.split('<')[0])

                        if ',' in el:
                            urls.append(el.split(',')[0])

                        if '!' in el:
                            urls.append(el.split('!')[0])

                        else:
                            urls.append(el.strip())

                except (NoSuchElementException, StaleElementReferenceException):
                    continue

                try:
                    for el in re.findall('@(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                         element.text):
                        if '<' in el:
                            urls.append(el.split('<')[0])

                        if ',' in el:
                            urls.append(el.split(',')[0])

                        if '!' in el:
                            urls.append(el.split('!')[0])

                        else:
                            urls.append(el.strip())

                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            actions = ActionChains(driver)
            actions.send_keys(Keys.PAGE_UP).perform()

            t1 = time()
            if t1 - t0 > TIME_SCROLL_SECONDS:
                break

        sleep(5)

        for i in range(0, len(urls)):
            if urls[i][-1] == '.':
                urls[i] = urls[i][:-1]

        urls = list(dict.fromkeys(urls))
        print('Length of scraped unverified links: ', len(urls))

        for username in urls:
            if 'http' in username:
                is_exist(username.split('/')[-1], count)
            elif '@' in username:
                is_exist(username[1:], count)
            else:
                is_exist(username, count)
    except:
        pass

def execute_driver():

    options = webdriver.ChromeOptions()

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.headless = False
    options.binary_location = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get('https://web.telegram.org/k')
        sleep(30)

        count = 1
        for link in get_links():
            work_with_group(driver, link, count)
            sleep(3)

        while True:
            if os.path.exists(f'data/groups_{count}.txt'):
                links = []
                with open(f'data/groups_{count}.txt', 'r') as f:
                    for line in f:
                        links.append(line.rstrip('\n'))

                if len(links) != 0:
                    for link in links:
                        work_with_group(driver, link, count + 1)
                else:
                    break

                count += 1
                sleep(3)

            else:
                break

        files = glob.glob('data/*')
        for f in files:
            os.remove(f)

        print('End of working!')
    finally:
        driver.quit()

def main():
    with open('output.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Group Link', 'Members'
        ])

    execute_driver()

if __name__ == '__main__':
    main()