import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


def parse_availability_table(table):
    availability_data = []
    rows = table.find_all('tr')

    # Find the second row and extract dates from <button> tags with the "aria-label" attribute
    date_row = rows[1]
    date_columns = date_row.find_all('th')
    dates = [col.find('button')['aria-label'] for col in date_columns if col.find('button') and col.find('button').has_attr('aria-label')]

    # Iterate through the data rows (skip the first two rows, which are the header and date rows)
    for row in rows[2:]:
        # Get the site number from the <th> tag with class "site-id-wrap camping-site-name-cell"
        site_number_tag = row.find('th', class_='site-id-wrap camping-site-name-cell')
        site_number = site_number_tag.get_text(strip=True) if site_number_tag else ''

        cols = row.find_all('td')

        # Check if the row has at least two columns (site loop and date)
        if len(cols) >= 2:
            # Get the site loop from the first column
            site_loop = cols[0].get_text(strip=True)

            # Iterate through the remaining columns (dates)
            for date, col in zip(dates, cols[1:]):
                col_classes = col.get('class')
                #print(col_classes)
                status = 'available' if col_classes and 'available' in col_classes else 'unavailable'
                #print(status)
                availability_data.append({
                    'site_number': site_number,
                    'site_loop': site_loop,
                    'date': date,
                    'status': status
                })

    return availability_data





def fetch_campsite_availability(campground_id):
    base_url = f'https://www.recreation.gov/camping/campgrounds/{campground_id}'
    availability_data = []

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run the browser in headless mode
    chrome_service = ChromeService(executable_path='/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get(base_url)

  
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'availability-table'))
        )

    availability_data = []
    days_fetched = 0
    max_days = 4 * 30  # 4 months

    while days_fetched < max_days:
        # Fetch the availability table
        availability_table = BeautifulSoup(driver.page_source, "html.parser").find("table", {'id': 'availability-table'})
        availability_data.extend(parse_availability_table(availability_table))

        # Click the next button
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testing-hook="nextDays"]')
        next_button.click()

        # Wait for the table to update

        days_fetched += 5

    driver.quit()
    return availability_data
def print_availability_data(data):
    print("Campsite availability:")
    for campsite in data:
        if campsite['status'] == 'available':
            print(f"{campsite['site_number']} ({campsite['site_loop']}): {(campsite['date'])}")


# Replace this with a valid campground ID
campground_id = '232755'
availability_data = fetch_campsite_availability(campground_id)
print_availability_data(availability_data)
#print(availability_data)
# Print the fetched availability data
