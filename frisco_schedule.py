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


frisco_url = 'https://www.frisco.pl/'
zaloguj_sie = (By.XPATH, '//a[@class="button cta" and contains(.,"Zaloguj się")]')
login_popup = (By.XPATH, '//div[@class="popup_box login"]')
email = (By.CSS_SELECTOR, 'input[name="username"]')
password = (By.ID, 'loginPassword')
submit = (By.CSS_SELECTOR, 'input.button.cta.login.large')
logged_surname = (By.XPATH, '//span[@class="surname" and contains(.,"Ramuk")]')
reservation_btn = (By.CSS_SELECTOR, '.header_delivery-inner.with-chevron')


class Frisco:
    def __init__(self, driver: webdriver):
        self.browser = driver

    def login(self, username, password):
        pass

