from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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