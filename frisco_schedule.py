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
import lxml
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
from gazpacho import Soup


frisco_url = 'https://www.frisco.pl/'
info_popup = (By.CSS_SELECTOR, 'div.fixed-popup.image-popup')
close_info_popup = (By.CSS_SELECTOR, 'a.close img')
zaloguj_sie = (By.XPATH, '//*[@class="button cta" and contains(.,"Zaloguj")]')
login_popup = (By.XPATH, '//div[@class="popup_box login"]')
email_field = (By.CSS_SELECTOR, 'input[name="username"]')
password_field = (By.ID, 'loginPassword')
submit = (By.CSS_SELECTOR, 'button[type="submit"]')
logged_surname = (By.XPATH, '//*[contains(@class, "logged-in") and contains(.,"Ramuk")]')
reservation_btn = (By.XPATH, '//*[contains(@class, "header-delivery")]')
kolejna_rezerwacja = (By.XPATH, '//*[contains(@class, "button") and contains(.,"Kolejna rezerwacja")]')
edytuj_button = (By.XPATH, '//div[@class="button secondary cta" and contains(., "Edytuj")]')
termin_dostawy_header = (By.XPATH, '//h4[contains(.,"Wybierz termin dostawy")]')
schedule_panel = (By.XPATH, '//div[contains(@class, "reservation-selector_section delivery-reservation-box")]')


class Frisco(BasePage):

    miesiace = ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paz', 'lis', 'gru']

    def get_month_no_from_text(self, month: str):
        return Frisco.miesiace.index(month) + 1

    def get_page(self):
        self.get(frisco_url)
        # self.wait_until_visible(10,info_popup)
        # close_elem = self.wait_until_element_visible(5, close_info_popup)
        # close_elem.click()
        self.wait_until_element_visible(10, zaloguj_sie)

    def login(self, username, password):
        self.wait_until_element_visible(10, zaloguj_sie).click()
        self.wait_until_element_visible(10, login_popup).click()        
        email_elem = self.find_element(*email_field)
        pass_elem = self.find_element(*password_field)
        email_elem.send_keys(username)
        pass_elem.send_keys(password)

        submit_btn = self.wait_until_element_visible(5, submit)
        submit_btn.click()
        self.wait_until_element_visible(10, logged_surname)

    def reservation(self):
        self.wait_until_element_visible(10, reservation_btn).click()
        time.sleep(5)
        # self.wait_until_element_visible(3, edytuj_button).click()
        self.wait_until_element_visible(3, kolejna_rezerwacja).click()
        time.sleep(2)
        schedule_elem = self.wait_until_element_visible(5, schedule_panel)
        
        self.available_dates = self.scrape_available_days()


        image = self.take_screenshot_of_element(schedule_elem)
        image_file = 'frisco_schedule.png'
        with open(image_file, 'wb') as f:
            f.write(image)

    def scrape_available_days(self):
        soup = Soup(self.page_source)
        reservation_box = soup.find('div', {'class': 'delivery-reservation-box'})
        month_switch = reservation_box.find('div', {'class': 'month-switcher'})
        month, year = month_switch.text.split()[0], month_switch.text.split()[-1]
        days = reservation_box.find('div', {'class': 'days'}).find('div', {'class': 'day active'}, partial=False)
        available_days = [day.text for day in days] if type(days) is list else [days.text]
        month_numeric = self.get_month_no_from_text(month)
    
        return [datetime.strptime(f'{day}-{month_numeric}-{year}', '%d-%m-%Y') for day in available_days]

    def get_available_dates_within(self, days=10):
        return [av_date.strftime('%d-%m-%Y') 
                for av_date in self.available_dates
                if av_date.date() < (datetime.now() + timedelta(days=days)).date()
                ]


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