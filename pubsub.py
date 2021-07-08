import os
from dotenv import load_dotenv
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

load_dotenv()

opts = ChromeOptions()
opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-sh-usage")
opts.add_argument("--window-size=1920,1080")
opts.add_argument('--disable-dev-shm-usage')
driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=opts)

#Sub of the Week
sotw = ''

def get_sub_of_the_week():
    global sotw
    i = 0
    while i < 3:
        print('Fetching Sub of the Week...')
        try:
            set_publix_store()
            driver.find_element_by_xpath("//a[@id='deli']").click()
            sotw = driver.find_element_by_xpath("//div[contains(text(),'Whole')][contains(text(),'Sub')]").text
            print('Sub successfully retrieved.')
            break
        except NoSuchElementException as e:
            print(e)
            print('There was an error while retrieving the sub of the week.')
        i += 1
    return sotw

def get_sub():
    if sotw != '':
        print('Sub already retrieved.')
        return sotw
    else:
        return get_sub_of_the_week()

def set_publix_store():
    driver.get('https://www.publix.com')
    try:
        driver.find_element_by_xpath("//div[contains(@class, 'store-search-toggle')]//button").click()
        driver.find_element_by_xpath("//input[@name='ZIP or City, State or store number']").send_keys("30301")
        driver.find_element_by_xpath("//input[@name='ZIP or City, State or store number']").send_keys(Keys.ENTER)
        driver.implicitly_wait(4)
        driver.find_element_by_xpath("//button[contains(text(),'Choose Store')]").click()
        driver.get('https://www.publix.com/savings/weekly-ad')
        driver.implicitly_wait(4)
        print('Store selected.')
    except NoSuchElementException as e:
        print(e)
        print('Store already selected.')