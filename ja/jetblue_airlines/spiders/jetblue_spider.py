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

class JetblueSpider(scrapy.Spider):
    name = "jetblue_spider"
    allowed_domains = ["www.jetblue.com"]
    start_urls = ["https://www.jetblue.com/"]

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
                # # # ['MCO', 'ATL'],
                # # # ['LAX', 'LAS'],
                # # # ['ORD', 'LGA'],

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

    def sleep(self):
        time.sleep(random.uniform(1, 3))

    def wait_for_element(self, driver, by, value, timeout=50):
        element_present = EC.presence_of_element_located((by, value))
        WebDriverWait(driver, timeout).until(element_present)

    def click_element(self, wait, by, value):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def send_keys_to_element(self, wait, by, value, keys):
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.clear() 
        element.send_keys(keys)

    def click_accept_cookies(self, driver): # Doesn't work
        button = driver.find_element_by_xpath('//a[contains(@class, "call") and text()="Accept All Cookies"]')
        driver.execute_script("arguments[0].click();", button)

    def change_date_format(self, date_string, usage):
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        if usage == 'filename':
            format = '%Y%m%d'
        else:
            format = '%a %b %d'

        formatted_date = date_object.strftime(format)
        return formatted_date
    
    def get_today_date(self):
        return date.today().strftime("%Y%m%d")
    
    def one_way(self, wait):
        self.click_element(wait, By.XPATH, '//div[contains(@class, "dropdown-text") and text()=" Roundtrip "]')
        self.sleep()
        self.click_element(wait, By.XPATH, '//div[contains(@class, "body") and .//span[text()=" One-way "]]')
        self.sleep()

    def navigate_location(self, wait, depart_loc, arrive_loc):
        try:
            self.send_keys_to_element(wait, By.ID, 'jb-autocomplete-1-search', f'{depart_loc}')
            self.send_keys_to_element(wait, By.ID, "jb-autocomplete-1-search", Keys.ENTER)
        except:
            try:
                self.send_keys_to_element(wait, By.ID, 'jb-autocomplete-3-search', f'{depart_loc}')
                self.send_keys_to_element(wait, By.ID, "jb-autocomplete-3-search", Keys.ENTER)
            except Exception as e:
                print(f"Both methods failed. Reason: {e}")

        self.sleep()

        try:
            self.send_keys_to_element(wait, By.ID, 'jb-autocomplete-2-search', f'{arrive_loc}')
            self.send_keys_to_element(wait, By.ID, "jb-autocomplete-2-search", Keys.ENTER)
        except:
            try:
                self.send_keys_to_element(wait, By.ID, 'jb-autocomplete-4-search', f'{arrive_loc}')
                self.send_keys_to_element(wait, By.ID, "jb-autocomplete-4-search", Keys.ENTER)
            except Exception as e:
                print(f"Both methods failed. Reason: {e}")

        self.sleep()

    def navigate_date(self, wait, date):
        try:
            self.click_element(wait, By.ID, 'jb-date-picker-input-id-0')
            self.send_keys_to_element(wait, By.ID, 'jb-date-picker-input-id-0', date)
        except:
            try:
                self.click_element(wait, By.ID, 'jb-date-picker-input-id-2')
                self.send_keys_to_element(wait, By.ID, 'jb-date-picker-input-id-2', date)
            except Exception as e:
                print(f"Both methods failed. Reason: {e}")

    def select_flight(self, wait):
        try:
            self.click_element(wait, By.CSS_SELECTOR, 'button[data-qaid="searchFlight"]')
        except:
            self.click_element(wait, By.XPATH, "//button[contains(@class, 'jb-button-primary') and contains(., 'Search flights')]")


    def navigate(self, wait, date):
        self.sleep()
        self.navigate_date(wait, date)
        self.sleep()
        self.select_flight(wait)
        self.sleep()

    def change_to_miles(self, wait):
        self.click_element(wait, By.XPATH, '//span[contains(@class, "charcoal") and text()="Use TrueBlue points"]')
        self.sleep()

    def scrape_page(self, driver, filename):
        self.sleep()

        directory = f'./data/{self.get_today_date()}'
        if not os.path.exists(directory):
            os.makedirs(directory)

   
        self.wait_for_element(driver, By.XPATH, '//div[@class="din ng-star-inserted" and text()=" Select your departing flight "]')


        self.sleep()

        html = driver.page_source

        with open(f'{directory}/{filename}', 'w') as f:
            f.write(html)

        self.sleep()

    def looping(self, wait, driver, miles_or_cash):
        MAX_RETRIES = 5

        if miles_or_cash == 'miles':
            self.change_to_miles(wait)

        for route in self.routes:
            self.navigate_location(wait, route[0], route[1])
            for date in self.dates:
                retries = 0
                while retries < MAX_RETRIES:
                    try:
                        self.navigate(wait, self.change_date_format(date, usage="navigate"))
                        self.sleep()
                        self.scrape_page(driver=driver, filename=f'ja_{self.get_today_date()}_{self.change_date_format(date, usage="filename")}_{route[0]}_{route[1]}_{miles_or_cash}.html')
                        self.sleep()
                        break  # Exit the while loop if the scraping is successful
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
        time.sleep(5)
        self.one_way(wait)

        self.looping(wait, driver, 'cash')
        self.looping(wait, driver, 'miles')