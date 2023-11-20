import scrapy
import time
import random
import os

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import date, datetime

class DeltaSpider(scrapy.Spider):
    name = "delta_spider"
    allowed_domains = ["www.delta.com"]
    start_urls = ["https://www.delta.com/"]

    dates = [
                # "16 November 2023, Thursday",
                # "17 November 2023, Friday",
                # "18 November 2023, Saturday",
                # "19 November 2023, Sunday",
                "20 November 2023, Monday",
                "21 November 2023, Tuesday",
                "22 November 2023, Wednesday",
                "23 November 2023, Thursday",
                "24 November 2023, Friday",
                "25 November 2023, Saturday",
                "26 November 2023, Sunday",
                "27 November 2023, Monday"
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

    def sleep(self):
        time.sleep(random.uniform(1, 4))
    
    def wait_for_element(self, driver, by, value, timeout=100):
        element_present = EC.presence_of_element_located((by, value))
        WebDriverWait(driver, timeout).until(element_present)

    def click_element(self, wait, by, value):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def send_keys_to_element(self, wait, by, value, keys):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.send_keys(keys)

    def click_available_element(self, wait, element, one, two):
        try:
            self.click_element(wait, element, one)
        except:
            self.click_element(wait, element, two)

    def one_way(self, wait):
        self.sleep()
        self.click_element(wait, By.CSS_SELECTOR, "#selectTripType-val")
        self.sleep()
        self.click_element(wait, By.ID, "ui-list-selectTripType1")
        self.sleep()

    def submit(self, wait):
        self.sleep()
        self.click_element(wait, By.ID, "btn-book-submit")
        self.sleep()

    def navigate_date(self, wait, date):
        self.sleep()
        self.click_available_element(wait, By.ID, "input_returnDate_1", "input_departureDate_1")
        self.sleep()
        self.click_element(wait, By.CSS_SELECTOR, f'a[aria-label="{date}"]')
        self.sleep()
        self.click_element(wait, By.XPATH, '//button[@aria-label="done"]')
        self.sleep()

    def navigate_location(self, wait, depart_loc, arrive_loc):
        self.sleep()
        self.click_element(wait, By.ID, "fromAirportName")
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'search_input', f'{depart_loc}')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'search_input', Keys.ENTER)
        self.sleep()
        self.click_element(wait, By.ID, "toAirportName")
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'search_input', f'{arrive_loc}')
        self.sleep()
        self.send_keys_to_element(wait, By.ID, 'search_input', Keys.ENTER)
        self.sleep()

    def change_to_miles(self, wait):
        self.sleep()
        self.click_element(wait, By.XPATH, "//a[@aria-label='Show Price In Miles']")
        self.sleep()

    def scrape_page(self, driver, filename):
        directory = f'./data/{self.get_today_date()}'
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.sleep()
        self.wait_for_element(driver, By.XPATH, "//a[@aria-label='Show Price In Miles']")
        
        self.sleep()
        html = driver.page_source
        self.sleep()

        with open(f'{directory}/{filename}', 'w') as f:
            f.write(html)
        
    def change_date_format(self, date_string):
        date_object = datetime.strptime(date_string, "%d %B %Y, %A")
        formatted_date = date_object.strftime('%Y%m%d')
        return formatted_date
    
    def get_today_date(self):
        return date.today().strftime("%Y%m%d")

    def parse(self, response):
        driver = response.request.meta["driver"]
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)

        MAX_RETRIES = 5

        self.sleep()
        self.one_way(wait)
        self.sleep()

        for route in self.routes:
            self.sleep()
            self.navigate_location(wait, route[0], route[1])
            self.sleep()
            for date in self.dates:
                retries = 0
                while retries < MAX_RETRIES:
                    try:
                        self.sleep()
                        self.navigate_date(wait, date)
                        self.sleep()
                        self.submit(wait)
                        self.sleep()
                        self.scrape_page(driver=driver, filename=f'da_{self.get_today_date()}_{self.change_date_format(date)}_{route[0]}_{route[1]}_cash.html')
                        self.sleep()
                        self.change_to_miles(wait)
                        self.sleep()
                        self.scrape_page(driver=driver, filename=f'da_{self.get_today_date()}_{self.change_date_format(date)}_{route[0]}_{route[1]}_miles.html')
                        self.sleep()
                        break
                    except Exception as e:
                        print(f"Scrape failed for date {date} due to {e}. Attempt {retries + 1}/{MAX_RETRIES}")
                        retries += 1
                        if retries == MAX_RETRIES:
                            print(f"Max retries reached for date {date}. Moving on to next date.")
                        self.sleep()
                        driver.get(self.start_urls[0])
                        self.sleep()
                self.sleep()
                driver.get(self.start_urls[0])
                self.sleep()









        