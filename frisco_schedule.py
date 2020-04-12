from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
# import lxml
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import argparse
import requests
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os
from browser import BasePage


frisco_url = 'https://www.frisco.pl/'
info_popup = (By.CSS_SELECTOR, 'div.fixed-popup.image-popup')
close_info_popup = (By.CSS_SELECTOR, 'a.close img')
zaloguj_sie = (By.XPATH, '//a[@class="button cta" and contains(.,"Zaloguj")]')
login_popup = (By.XPATH, '//div[@class="popup_box login"]')
email = (By.CSS_SELECTOR, 'input[name="username"]')
password = (By.ID, 'loginPassword')
submit = (By.CSS_SELECTOR, 'input.button.cta.login.large')
logged_surname = (By.XPATH, '//span[@class="surname" and contains(.,"Ramuk")]')
reservation_btn = (By.CSS_SELECTOR, '.header_delivery-inner.with-chevron')


class Frisco(BasePage):

    def get_page(self):
        self.driver.get(frisco_url)
        self.driver.wait_until_visible(10,info_popup)
        close_elem = self.driver.wait_until_element_visible(5, close_info_popup)
        close_elem.click()
        self.driver.wait_until_element_visible(10, zaloguj_sie)

    def login(self, username, password):
        self.driver.wait_until_element_visible(10, zaloguj_sie).click()
        self.driver.wait_until_element_visible(10, login_popup).click()        
        email_elem = self.find_element(*email)
        pass_elem = self.find_element(*password)
        email_elem.send_keys(username)
        pass_elem.send_keys(password)

        self.find_element(*submit).click()
        self.driver.wait_until_element_visible(10, logged_surname)


if __name__ == "__main__":
    username = os.environ.get('ARG_USERNAME')
    password = os.environ.get('ARG_PASSWORD')
    notifip = os.environ.get('ARG_NOTIFIP')

    browser = BasePage(initialize_webdriver())
    frisco = Frisco(browser)
    frisco.get_page()
    frisco.login('krzysztof_rrr@wp.pl', 'EdekFruniak2')