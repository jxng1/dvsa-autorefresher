import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

# --- Configuration ---
DVSA_URL = "https://driverpracticaltest.dvsa.gov.uk/login"
LICENSE_NUMBER = ""
POSTCODE = ""
TEST_REFERENCE = ""
REFRESH_INTERVAL = 30  # Refresh every 30 secs
PROXY_LIST = []  # Add your rotating proxies here
TEST_CENTRES_TO_CHECK = []  # Test centres to check for slots
PREFERRED_TEST_DATE = "12/05/2025"  # Preferred test date, script will look for a date before/equal to this date

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--incognito")
    # proxy = random.choice(PROXY_LIST) if PROXY_LIST else None
    # if proxy:
    #     options.add_argument(f'--proxy-server={proxy}')
    return uc.Chrome(options=options, use_subprocess=True)

driver = get_driver()
driver.set_window_position(2000, 300)
driver.set_window_size(800, 800)

def human_like_delay(min_time=0.1, max_time=0.3):
    time.sleep(random.uniform(min_time * 60, max_time * 60))

def fill_form():
    try:
        driver.get(DVSA_URL)
        time.sleep(30)
        
        human_like_delay()
                
        # Fill in form fields
        driver.find_element(By.ID, "driving-licence-number").send_keys(LICENSE_NUMBER)
        human_like_delay()
        driver.find_element(By.ID, "application-reference-number").send_keys(TEST_REFERENCE)
        human_like_delay()
        
        # Submit login form
        driver.find_element(By.ID, "booking-login").click()
        human_like_delay()
        
        # Change test centre form
        driver.find_element(By.ID, "test-centre-change").click()
        human_like_delay()
        
        # Fill in test centre form
        driver.find_element(By.ID, "test-centres-input").send_keys(Keys.CONTROL, 'a')
        driver.find_element(By.ID, "test-centres-input").send_keys(Keys.BACKSPACE)
        human_like_delay()
        driver.find_element(By.ID, "test-centres-input").send_keys(POSTCODE)
        human_like_delay()
        
        # Submit test centre form
        driver.find_element(By.ID, "test-centres-submit").click()
        human_like_delay()
        
        # Expand search
        driver.find_element(By.ID, "fetch-more-centres").click()
        human_like_delay()
        
        # Check for earlier slots
        check_and_book_slot()
    except Exception as e:
        print(f"Error: {e}")

def check_and_book_slot():
    try:
        human_like_delay()
                
        available_slots = driver.find_elements(By.CLASS_NAME, "test-centre-details")  # Adjust selector if needed
        if available_slots:
            for slot in available_slots:
                texts = slot.text.split('–')
                test_centre = texts[0].strip()
                test_available_string = texts[1].strip()
                
                if (test_centre in TEST_CENTRES_TO_CHECK and "available tests" in texts[1]):
                    # There's a test available, check against time that is requested
                    print("Found test at desired centre")
                    
                    date_string = test_available_string.split(" ")[-1]
                    
                    date_preferred = time.strptime(PREFERRED_TEST_DATE, "%d/%m/%Y")
                    date_polled = time.strptime(date_string, "%d/%m/%Y")
                    if date_polled <= date_preferred:
                        # Found test before desired date, 
                        # Click on the element to get to the calendar page
                        slot.click()
        else:
            print("No earlier slots available.")
    except Exception as e:
        print(f"Error checking slots: {e}")
        
fill_form()
try:
    count = 0
    while True:
        count += 1
        check_and_book_slot()
        time.sleep(REFRESH_INTERVAL)
        print(f"Refreshing page... {count}")
        driver.refresh()
except KeyboardInterrupt:
    driver.quit()
    exit()