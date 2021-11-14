import os
import re
import requests
import csv
import time
import html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from prettytable import PrettyTable

def create_csv():
    global csv_name
    global dirname
    dirname = r'%s' % os.path.dirname(__file__)
    csv_name = dirname + '/data.csv'
    with open(csv_name, mode='w') as data:
        writer = csv.writer(data, delimiter='*', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        entry = ["State", "City/County", "Ordinance", "Site"]
        writer.writerow(entry)

def make_driver():
    driverpath = dirname + r'/chromedriver'
    options = webdriver.ChromeOptions()
    global driver
    driver = webdriver.Chrome(options=options, executable_path=driverpath)

def write_entry(state, county, link, site):
    with open(csv_name, mode='a') as data:
        writer = csv.writer(data, delimiter='*', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        entry = [state, county, link, site]
        writer.writerow(entry)

def general_code():
    def get_counties():
        page = requests.get('https://www.generalcode.com/text-library/')
        soup = BeautifulSoup(page.text, 'html.parser')
        states = soup.find_all('div', class_=re.compile('state'))
        for state in states:
            state_name = state.find('h2', class_='stateTitle').text
            cities = state.find_all('div', class_='listItem')
            for city in cities:
                try:
                    county = city.find('div', class_='codeCounty').text
                except Exception:
                    county = ""
                city_link = city.find('a', class_='codeLink')
                write_entry(state_name, city_link.text + county, city_link['href'], "General Code")
    get_counties()

def municode():
    def get_states():
        make_driver()
        driver.get('https://library.municode.com')
        state_links = []
        state_path = '/html/body/div[1]/div[2]/ui-view/div[2]/section/div/div[2]/div[{}]/ul/li[{}]/a'
        for i in range(3, 23):
            for j in range(1, 11):
                try:
                    state = driver.find_element(By.XPATH, state_path.format(i, j))
                    state_links.append(state.get_attribute('href'))
                except NoSuchElementException:
                    break
        return state_links
    def get_counties(state_link):
        driver.get(state_link)
        county_path = '/html/body/div[1]/div[2]/ui-view/div[2]/section/div/div/div[{}]/ul/li/a'
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, county_path.format(2))))
        except TimeoutException:
            print('Unable to load ' + state_link + '.')
            return
        for i in range(2, 29):
            try:
                counties = driver.find_elements(By.XPATH, county_path.format(i))
                state = state_link[len(state_link) - 2 : len(state_link)].upper()
                for county in counties:
                    write_entry(state, county.text, county.get_attribute('href'), "Municode")
            except NoSuchElementException:
                break
    state_links = get_states()
    for link in state_links:
        get_counties(link)
    driver.quit()

def amlpc():
    def get_regions():
        page = requests.get('https://codelibrary.amlegal.com/')
        soup = BeautifulSoup(page.text, 'html.parser')
        states = soup.find_all('a', href=re.compile('/regions/'))
        for state in states:
            link = 'https://codelibrary.amlegal.com' + state['href']
            page = requests.get(link)
            soup = BeautifulSoup(page.text, 'html.parser')
            counties = soup.find_all('a', href=re.compile('/codes/'))
            for county in counties:
                link = 'https://codelibrary.amlegal.com' + county['href']
                write_entry(state.text, county.text, link, "Americal Legal Publishing")
    get_regions()

def codebook():
    def get_states():
        page = requests.get('https://www.codebook.com/listing/#')
        soup = BeautifulSoup(page.text, 'html.parser')
        states = soup.find_all('div', class_='listing-region')
        states = states[3 : len(states)] #removes Canada, tribes, and special regions
        for state in states:
            state_name = state.find('h1', class_='state-name').text
            state_name = state_name[0] + state_name[1 : len(state_name)].lower()
            counties = state.find_all('a', rel='noreferrer noopener')
            for county in counties:
                write_entry(state_name, county.text, county['href'], "Codebook")
    get_states()

def franklin_legal():
    def get_counties():
        page = requests.get('http://www.franklinlegal.net/search-codes')
        soup = BeautifulSoup(page.text, 'html.parser')
        counties = soup.find_all('option', target=re.compile('blank'))
        counties = counties[1 : len(counties)]
        for county in counties:
            if check_exists(county['value']) == True:
                write_entry("Texas", county.text, county['value'], "Franklin Legal")
            else:
                continue
    def check_exists(ordinance_link):
        return True
    get_counties()

def mtas():
    def get_counties():
        page = requests.get('https://www.mtas.tennessee.edu/charters_bycity_files')
        soup = BeautifulSoup(page.text, 'html.parser')
        counties = soup.find_all('a', href=re.compile('/city/'))
        for county in counties:
            page = requests.get('https://www.mtas.tennessee.edu' + county['href'])
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                link = soup.find_all('a', type=re.compile('application/pdf'))
                link = link[len(link) - 1]['href']
            except Exception:
                link = ""
            write_entry("Tennessee", county.text, link, "MTAS")
    get_counties()

def quality_code():
    def get_counties():
        page = requests.get('https://www.qcode.us/codes.html')
        soup = BeautifulSoup(page.text, 'html.parser')
        counties = soup.find_all('a', href=re.compile('view=desktop'))
        for county in counties:
            state = re.search('([A-Z]){2}', county.text).group(0)
            county_name = county.text[0 : county.text.index(',')]
            write_entry(state, county_name, county['href'], "Quality Code")
    get_counties()

def clerkbase():
    def get_counties():
        make_driver()
        driver.get("https://clerkshq.com/")
        county_path = "/html/body/div/main/div/ul/li[{}]/a"
        counties = []
        for i in range(1, 35):
            county = driver.find_element(By.XPATH, county_path.format(i))
            state = str(county.get_attribute("href"))
            state = state[len(state) - 2 : len(state)].upper()
            write_entry(state, county.text, county.get_attribute("href"), "ClerkBase")
        driver.quit()
    get_counties()

def ranson():
    def get_counties():
        make_driver()
        driver.get("https://www.ransonfinancial.com/code-library/")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        counties = soup.find_all("a", href=re.compile(".citycode.net"))
        for county in counties:
            state = county.text
            state = state[state.index(",") + 2 : len(state)]
            county_name = county.text[0 : county.text.index(",")]
            write_entry(state, county_name, county["href"], "Ranson Citycode")
        driver.quit()
    get_counties()

def drake():
    def get_counties():
        page = requests.get("https://libguides.law.drake.edu/c.php?g=150956&p=992837")
        soup = BeautifulSoup(page.text, 'html.parser')
        counties = soup.find_all("a", target="_blank")
        for county in counties:
            write_entry("Iowa", county.text, county['href'], "Drake University Law Library")
    get_counties()

def nebraska_access():
    def get_counties():
        make_driver()
        driver.get("http://nebraskaccess.nebraska.gov/municipalcodes.asp")
        county_path = "/html/body/div[2]/div/div/div[3]/div/div[1]/div/ul[1]/li[{}]/a"
        for i in range(1, 100):
            try:
                county = driver.find_element(By.XPATH, county_path.format(i))
                county_name = county.text
                try:
                    if county_name.index("American Legal Publishing") >= 0: 
                        continue
                except ValueError:
                    county_name = county_name
                try:
                    county_name = county_name[0 : county_name.index("Code") - 1]
                except ValueError:
                    county_name = county_name
                try:
                    county_name = county_name[0 : county_name.index("Municipal") - 1]
                except ValueError:
                    county_name = county_name
                try:
                    county_name = county_name[0 : county_name.index("Ordinances") - 1]
                except ValueError:
                    county_name = county_name
                write_entry("Nebraska", county_name, county.get_attribute("href"), "Nebraska Access")
            except NoSuchElementException:
                break
        driver.quit()
    get_counties()

def make_html():
    a = open(csv_name, 'r')
    a = a.readlines()
    l1 = a[0]
    l1 = l1.split('*')
    t = PrettyTable([l1[0], l1[1], l1[2], l1[3]])
    for i in range (1, len(a)):
        try:
            row = a[i].split('*')
            link = "<a href=\'" + row[2] + "\'>" + row[2] + "</a>"
            t.add_row([row[0], row[1], link, row[3]])
        except Exception:
            print(i)
    code = t.get_html_string(format=True)
    code = html.unescape(code)
    html_file = open('ordinances.html', 'w')
    html_file = html_file.write(code)

def main():
    create_csv()
    make_driver()
    general_code()
    municode()
    amlpc()
    codebook()
    franklin_legal()
    mtas()
    quality_code()
    ranson()
    clerkbase()
    drake()
    nebraska_access()
    make_html()

if __name__ == '__main__':
    main()