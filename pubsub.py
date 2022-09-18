import os
from dotenv import load_dotenv
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException

load_dotenv()

opts = ChromeOptions()
opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-sh-usage")
opts.add_argument("--window-size=1920,1080")
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--ignore-certificate-errors')
opts.add_argument('--allow-running-insecure-content')
driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=opts)
driver.execute_cdp_cmd(
    "Browser.grantPermissions",
    {
        "origin": "https://www.publix.com/",
        "permissions": ["geolocation"]
    },
)
driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
    "latitude": 33.75074105969834,
    "longitude": -84.39513846451307,
    "accuracy": 100
})


#Sub of the Week
sotw = ''

def fetch_sub_of_the_week():
    global sotw
    i = 0
    while i < 3:
        print('Fetching Sub of the Week...')
        try:
            driver.get('https://www.publix.com/savings/weekly-ad/view-all?keyword=sub')
            driver.implicitly_wait(3)
            sotw = driver.find_element("xpath", "//span[contains(text(),'Whole')][contains(text(),'Sub')]").text      
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
        return fetch_sub_of_the_week()