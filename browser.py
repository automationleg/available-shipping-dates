from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage(webdriver.Chrome):

    def __init__(self, options, remote: bool = 'False'):
        if remote:
            webdriver.Remote.__init__(command_executor='http://127.0.0.1:4444/wd/hub', options=options)
        else:
            webdriver.Chrome.__init__(self, options=options)

    def wait_until_visible(self, wait_time, *locator, error_message=''):
        return WebDriverWait(self, wait_time).until(
            EC.visibility_of_all_elements_located(*locator),
            message=f'{error_message}\n'
            f'Details: Element with the following locator "{locator}" was not displayed within {wait_time} seconds'
        )
