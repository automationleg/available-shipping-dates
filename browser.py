from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class BasePage(webdriver.Chrome):

    def __init__(self, driver):
        self.driver = driver

    def wait_until_visible(self, wait_time, *locator, error_message=''):
        return WebDriverWait(self, wait_time).until(
            EC.visibility_of_all_elements_located(*locator),
            message=f'{error_message}\n'
            f'Details: Element with the following locator "{locator}" was not displayed within {wait_time} seconds'
        )

    def wait_until_element_visible(self, wait_time, *locator, error_message=''):
        return WebDriverWait(self, wait_time).until(
            EC.visibility_of_element_located(*locator),
            message=f'{error_message}\n'
            f'Details: Element with the following locator "{locator}" was not displayed within {wait_time} seconds'
        )

def initialize_webdriver(remote=False):
    if remote:
        webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=set_chrome_options())
    else:
        webdriver.Chrome(options=set_chrome_options())

def set_chrome_options() -> Options:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('-disable-extensions')

    return chrome_options