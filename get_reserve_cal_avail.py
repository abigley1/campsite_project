import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import time



def fetch_campsite_availability_reserve_california(park_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run the browser in headless mode
    chrome_service = ChromeService(executable_path='/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=chrome_service, options=options)
    url = f"https://www.reservecalifornia.com/Web/#!park/{park_id}"
    driver.get(url)
    time.sleep(3)

    grid_container = driver.find_element(By.CSS_SELECTOR, '.grid.col-gap-8.row-gap-5.grid-cols-results')
    section_tiles = grid_container.find_elements(By.CSS_SELECTOR, '[class*="shadow-teal-input-shadow"]')

    for tile in section_tiles:
        section_name = tile.find_element(By.CSS_SELECTOR, '.font-bold').text
        availability_page_link = tile.get_attribute("href")

        print(f"Section Name: {section_name}")
        print(f"Availability Page Link: {availability_page_link}")

        # Go to the availability page
        driver.get(availability_page_link)
        time.sleep(3)
        # Find the availability table
        availability_table = driver.find_element(By.CSS_SELECTOR, '.w-full.lg\\:flex.lg\\:flex-col.lg\\:items-center.js-book-modal')
        rows = availability_table.find_elements(By.TAG_NAME, 'tr')
        print(availability_table)
        # Iterate through the table rows (excluding the header)
        rows = availability_table.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in rows[14:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            
            campsite_number = columns[0].text
            print(f"Campsite Number: {campsite_number}")
            
            #for i in range(1, len(columns)):
                #try:
                  #  button_title = columns[i].find_element(By.TAG_NAME, 'button').get_attribute('class')
                 #   if " available" in button_title:
                        #print(f"Day {i}: Available")
                 #   else:
                        #print(f"Day {i}: Not Available")
                #except IndexError:
                    #print(f"Day {i}: Data not found")
            #print("\n")

        # Check if there's a "Next Week" button and click it if it exists
        try:
            next_week_button = driver.find_element(By.XPATH, '//button[contains(@class, "bg-transparent")][contains(@class, "text-gray-04")][contains(@class, "font-light")][contains(@class, "flex")][contains(@class, "items-center")][contains(@class, "md:justify-center")][contains(@class, "justify-end")][contains(@class, "py-3")]')
            next_week_button.click()
            time.sleep(3)

            # Scrape availability for the next week (similar to the previous block)
            availability_table = driver.find_element(By.CSS_SELECTOR, '.w-full.lg:flex.lg:flex-col.lg:items-center.js-book-modal')
            rows = availability_table.find_elements(By.CSS_SELECTOR, 'tbody tr')
            for row in rows:
                columns = row.find_elements(By.CSS_SELECTOR, 'td')
                campsite_number = columns[0].text

                print(f"Campsite Number: {campsite_number}")

                for i in range(1, 8):
                    availability = columns[i].text
                    print(f"Day {i}: {availability}")

        except NoSuchElementException:
            print("No more weeks available.")
            pass

        # Return to the main park page before moving on to the next section
        driver.get(url)
        time.sleep(3)

    driver.quit()
    return section_data

# Test the function with a sample park ID
sample_park_id = '709'
fetch_campsite_availability_reserve_california(sample_park_id)
