import scrapy
import time
import random
import os

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime



class UnitedSpider(scrapy.Spider):
    name = "united_spider"
    allowed_domains = ["www.united.com"]
    start_urls = ["https://www.google.com"]

    dates = [
                "11/16/2023",
                "11/17/2023",
                "11/18/2023",
                "11/19/2023",
                "11/20/2023",
                "11/21/2023",
                "11/22/2023",
                "11/23/2023"
             ]
    
    routes = [
                ['JFK', 'LAX'],
                ['LAX', 'SFO'],
                ['ATL', 'MCO'],
                ['LAS', 'LAX'],
                ['LGA', 'ORD']
             ]


    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                # headers={'User-Agent': self.settings.get('USER_AGENT')}              
            )

    def load_start_url(self, driver):
        driver.get('https://www.united.com/en/us')

    def sleep(self):
        time.sleep(random.uniform(1, 3))

    def wait_for_element(self, driver, by, value, timeout=100):
        element_present = EC.presence_of_element_located((by, value))
        WebDriverWait(driver, timeout).until(element_present)

    def click_element(self, wait, by, value):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def send_keys_to_element(self, wait, by, value, keys):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.clear() 
        element.send_keys(keys)

    def change_date_format(self, date_string, usage):
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        if usage == 'filename':
            format = '%Y%m%d'
        else:
            format = '%b %d'

        formatted_date = date_object.strftime(format)
        return formatted_date
    
    def get_today_date(self):
        return date.today().strftime("%Y%m%d")


    def navigate(self, wait, depart_loc, arrive_loc, date):
        self.click_element(wait, By.CSS_SELECTOR, 'label[for="oneway"]')
        self.sleep()
        self.click_element(wait, By.ID, 'bookFlightOriginInput')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'bookFlightOriginInput', f'{depart_loc}')
        self.sleep()
        self.click_element(wait, By.ID, 'bookFlightDestinationInput')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'bookFlightDestinationInput', f'{arrive_loc}')
        self.sleep()
        self.click_element(wait, By.ID, 'DepartDate')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'DepartDate', date)
        self.sleep()
        self.click_element(wait, By.CSS_SELECTOR, 'button[aria-label="Find flights"]')
        self.sleep()

    def change_to_miles(self, wait):
        self.click_element(wait, By.XPATH, '//span[text()="Book with miles"]')
        self.sleep()

    def scrape_page(self, driver, filename):
        directory = './data/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.wait_for_element(driver, By.XPATH, '//div[contains(@class, "app-containers-Shopping-FlightSearchResultsContainer-styles__detailHeading--3nO7v")]/span')

        html = driver.page_source

        with open(f'{directory}/{filename}', 'w') as f:
            f.write(html)

    def looping(self, wait, driver, miles_or_cash):
        if miles_or_cash == 'miles':
            self.change_to_miles(wait)
        for route in self.routes:
            for date in self.dates:
                self.navigate(wait, route[0], route[1], self.change_date_format(date, usage="navigate"))
                self.sleep()
                if miles_or_cash == 'miles':
                    self.click_element(wait, By.ID, 'closeBtn')
                self.scrape_page(driver=driver, filename=f'ua_{self.get_today_date()}_{self.change_date_format(date, usage="filename")}_{route[0]}_{route[1]}_{miles_or_cash}.html')
                self.sleep()
                self.load_start_url(driver)
                self.sleep()

    def parse(self, response):
        driver = response.request.meta["driver"]
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        self.load_start_url(driver)

        # self.looping(wait, driver, 'cash')
        self.looping(wait, driver, 'miles')