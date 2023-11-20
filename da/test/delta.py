from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time, requests


def create_driver():
    return webdriver.Chrome(executable_path='chromedriver')


def navigate_to_page(driver, url):
    driver.get(url)


def click_element(wait, by, value):
    element = wait.until(EC.element_to_be_clickable((by, value)))
    element.click()


def send_keys_to_element(wait, by, value, keys):
    element = wait.until(EC.element_to_be_clickable((by, value)))
    element.send_keys(keys)

def scrape_data(url):
    html = requests.get(url);
    soup = BeautifulSoup(html, 'html.parser')

    flights = soup.find_all('div', class_='flight-results-grid ng-star-inserted')
    print(flights)

    for flight in flights:
        nonstop = flight.find('div', class_='flight-card-badge')
        if nonstop and 'Nonstop' in nonstop.get_text(strip=True):
            departure_location = flight.find('div', class_='flight-card-path__start').get_text(strip=True)
            arrival_location = flight.find('div', class_='flight-card-path__end').get_text(strip=True)
            departure_time, arrival_time = [time.get_text(strip=True) for time in flight.find_all('div', class_='schedule-time')]
            flight_duration = flight.find('div', class_='flight-duration').get_text(strip=True)
            flight_number = flight.find('span').get_text(strip=True)
            
            pricing_info = flight.find_all('div', class_='fare-cell-desktop')
            for price in pricing_info:
                class_name = price.find('div', class_='cell-brand-name').get_text(strip=True) if price.find('div', class_='cell-brand-name') else None
                fare = price.find('div', class_='fare-cell-miles-value').get_text(strip=True) if price.find('div', class_='fare-cell-miles-value') else None
                cash = price.find('span', class_='fare-cell-rounded-amount').get_text(strip=True) if price.find('span', class_='fare-cell-rounded-amount') else None
                
                print(f"Class: {class_name}, Miles: {fare}, Cash: ${cash}")
            
            print(f"Flight {flight_number} from {departure_location} to {arrival_location} departs at {departure_time} and arrives at {arrival_time}. Duration: {flight_duration}\n")

    

def main():
    driver = create_driver()
    navigate_to_page(driver, 'https://www.delta.com/')

    wait = WebDriverWait(driver, 10)

    click_element(wait, By.ID, "fromAirportName")
    send_keys_to_element(wait, By.ID, 'search_input', 'JFK')
    click_element(wait, By.CSS_SELECTOR, "li[data-index='0']")
    click_element(wait, By.ID, "toAirportName")
    send_keys_to_element(wait, By.ID, 'search_input', 'LAX')
    click_element(wait, By.CSS_SELECTOR, "li[data-index='0']")
    click_element(wait, By.CSS_SELECTOR, "#selectTripType-val")
    click_element(wait, By.ID, "ui-list-selectTripType1")
    click_element(wait, By.ID, "input_departureDate_1")
    click_element(wait, By.CSS_SELECTOR, 'a[aria-label="15 October 2023, Sunday"]')
    time.sleep(1)
    click_element(wait, By.CSS_SELECTOR, 'button[aria-label="done"]')
    click_element(wait, By.CSS_SELECTOR, "label[for='shopWithMiles']")
    click_element(wait, By.CSS_SELECTOR, "label[for='chkFlexDate']")
    click_element(wait, By.ID, "btn-book-submit")

    time.sleep(5)

    scrape_data(driver.page_source)

    time.sleep(5)




if __name__ == "__main__":
    main()
