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
from browser import *


frisco_url = 'https://www.frisco.pl/'
info_popup = (By.CSS_SELECTOR, 'div.fixed-popup.image-popup')
close_info_popup = (By.CSS_SELECTOR, 'a.close img')
zaloguj_sie = (By.XPATH, '//a[@class="button cta" and contains(.,"Zaloguj")]')
login_popup = (By.XPATH, '//div[@class="popup_box login"]')
email_field = (By.CSS_SELECTOR, 'input[name="username"]')
password_field = (By.ID, 'loginPassword')
submit = (By.CSS_SELECTOR, 'input.button.cta.login.large')
logged_surname = (By.XPATH, '//span[@class="surname" and contains(.,"Ramuk")]')
reservation_btn = (By.CSS_SELECTOR, '.header_delivery-inner.with-chevron')
edytuj_button = (By.XPATH, '//div[@class="button secondary cta" and contains(., "Edytuj")]')
termin_dostawy_header = (By.XPATH, '//h4[contains(.,"Wybierz termin dostawy")]')
schedule_panel = (By.XPATH, '//div[contains(@class, "reservation-selector_section delivery-reservation-box")]')


class Frisco(BasePage):


    def get_page(self):
        self.get(frisco_url)
        self.wait_until_visible(10,info_popup)
        close_elem = self.wait_until_element_visible(5, close_info_popup)
        close_elem.click()
        self.wait_until_element_visible(10, zaloguj_sie)

    def login(self, username, password):
        self.wait_until_element_visible(10, zaloguj_sie).click()
        self.wait_until_element_visible(10, login_popup).click()        
        email_elem = self.find_element(*email_field)
        pass_elem = self.find_element(*password_field)
        email_elem.send_keys(username)
        pass_elem.send_keys(password)

        self.find_element(*submit).click()
        self.wait_until_element_visible(10, logged_surname)

    def reservation(self):
        self.wait_until_element_visible(10, reservation_btn).click()
        time.sleep(5)
        self.wait_until_element_visible(3, edytuj_button).click()
        time.sleep(2)
        schedule_elem = self.wait_until_element_visible(5, schedule_panel)
        image = self.take_screenshot_of_element(schedule_elem)
        image_file = 'frisco_schedule.png'
        with open(image_file, 'wb') as f:
            f.write(image)



def send_file_to_openhab(filename, hostname):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname, username='vagrant')

    # SCPCLient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())

    scp.put(filename, '/etc/openhab2/html/sklepy_charmonogram/')


if __name__ == "__main__":
    username = os.environ.get('ARG_USERNAME')
    password = os.environ.get('ARG_PASSWORD')
    notifip = os.environ.get('ARG_NOTIFIP')

    frisco = Frisco()
    frisco.get_page()
    frisco.login(username, password)

    # check reservation
    frisco.reservation()

    #send file
    send_file_to_openhab('frisco_schedule.png', notifip)

    frisco.quit()