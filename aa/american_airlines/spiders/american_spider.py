import scrapy
import time
import random
import os

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime

class AmericanSpider(scrapy.Spider):
    name = "american_spider"
    allowed_domains = ["www.aa.com"]
    start_urls = ["https://www.aa.com/"]

    dates = [
                # "11/16/2023",
                # "11/17/2023",
                # "11/18/2023",
                # "11/19/2023",
                "11/20/2023",
                "11/21/2023",
                "11/22/2023",
                "11/23/2023",
                "11/24/2023",
                "11/25/2023",
                "11/26/2023",
                "11/27/2023"
             ]
    
    routes = [
                ['JFK', 'LAX'],
                ['SFO', 'LAX'],
                ['MCO', 'ATL'],
                ['LAX', 'LAS'],
                ['ORD', 'LGA'],

                ['LAX', 'JFK'],
                ['LAX', 'SFO'],
             ]


    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse                
            )

    def load_start_url(self, driver):
        driver.get(self.start_urls[0])
        driver.execute_script("window.scrollBy(0, 500)")

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

    def change_date_format(self, date_string):
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        formatted_date = date_object.strftime('%Y%m%d')
        return formatted_date
    
    def get_today_date(self):
        return date.today().strftime("%Y%m%d")

    def one_way(self, wait):
        self.sleep()
        self.click_element(wait, By.CSS_SELECTOR, 'label[for="flightSearchForm.tripType.oneWay"]')
        self.sleep()

    def navigate(self, wait, date):
        self.sleep()
        self.navigate_date(wait, date)
        self.sleep()
        self.select_flight(wait)
        self.sleep()

    def navigate_location(self, wait, depart_loc, arrive_loc):
        self.sleep()
        self.click_element(wait, By.ID, 'reservationFlightSearchForm.originAirport')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'reservationFlightSearchForm.originAirport', f'{depart_loc}')
        self.sleep()
        self.click_element(wait, By.ID, 'reservationFlightSearchForm.destinationAirport')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'reservationFlightSearchForm.destinationAirport', f'{arrive_loc}')
        self.sleep()  

    def navigate_date(self, wait, date):
        self.sleep()
        self.click_element(wait, By.ID, 'aa-leavingOn')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'aa-leavingOn', date)
        self.sleep()

    def select_flight(self, wait):
        self.sleep()
        self.click_element(wait, By.ID, 'flightSearchForm.button.reSubmit')
        self.sleep()

    def change_to_miles(self, wait):
        self.click_element(wait, By.CSS_SELECTOR, "label[for='flightSearchForm.tripType.redeemMiles']")
        self.sleep()

    def scrape_page(self, driver, filename):
        directory = f'./data/{self.get_today_date()}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.sleep()

        self.wait_for_element(driver, By.CSS_SELECTOR, 'h3.date')

        self.sleep()

        html = driver.page_source

        self.sleep()

        with open(f'{directory}/{filename}', 'w') as f:
            f.write(html)

        self.sleep()

    def looping(self, wait, driver, miles_or_cash):
        driver.execute_script("window.scrollBy(0, 500)")

        MAX_RETRIES = 5

        if miles_or_cash == 'miles':
            self.change_to_miles(wait)

        for route in self.routes:
            self.navigate_location(wait, depart_loc = route[0], arrive_loc = route[1])
            for date in self.dates:
                retries = 0
                while retries < MAX_RETRIES:
                    try:
                        self.navigate(wait, date)
                        self.sleep()
                        self.scrape_page(driver=driver, filename=f'aa_{self.get_today_date()}_{self.change_date_format(date)}_{route[0]}_{route[1]}_{miles_or_cash}.html')
                        self.sleep()
                        break
                    except Exception as e:
                        print(f"Scrape failed for date {date} due to {e}. Attempt {retries + 1}/{MAX_RETRIES}")
                        retries += 1
                        if retries == MAX_RETRIES:
                            print(f"Max retries reached for date {date}. Moving on to next date.")
                        self.load_start_url(driver)
                self.sleep()
                self.load_start_url(driver)
                self.sleep()

    def parse(self, response):
        driver = response.request.meta["driver"]
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)

        self.one_way(wait)

        self.looping(waitnot, driver, 'cash')
        self.looping(wait, driver, 'miles')