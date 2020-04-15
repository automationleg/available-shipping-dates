from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
import re
# import lxml
import pandas as pd
from datetime import datetime, timedelta
from browser import BasePage


apimarket_url = 'https://apimarket.pl/'
login_header = (By.XPATH, '//h3[text()="Masz już konto?"]')
zip_popup_close = (By.XPATH, '//div[contains(@class, "fancybox-overlay")]//a[@title="Close"]')
submit_zip_code = (By.XPATH, '//div[contains(@class, "fancybox-overlay")]//button[@type="submit"]')
terminy_dostaw = (By.CLASS_NAME, 'ard-top-time-slots')
times_table_popup = (By.CLASS_NAME, 'time-slots-popup')
next_days = (By.CLASS_NAME, 'ts-next')


class Apimarket(BasePage):

    def get_page(self):
        self.get(apimarket_url)
        time.sleep(5)

    def login(self, username, password):
        login = self.find_element_by_class_name('login')
        login.click()

        # wait for login form
        self.wait_until_visible(10, login_header)

        email_field = self.find_element_by_id('email').send_keys(username)
        pass_field = self.find_element_by_id('passwd').send_keys(password)
        time.sleep(1)
        self.find_element_by_id('SubmitLogin').click()


    def enter_zip_code(self, zipcode):
        # close any popup
        self.find_element_by_xpath('//input[@name="post_code"]').send_keys('05510')
        self.find_element(*submit_zip_code).click()
        # self.find_element(*zip_popup_close).click()
        time.sleep(3)


    def change_schedule_table(self, df):
        pd.options.display.width = 0

        updated_sched = df.copy(deep=True)
        updated_sched = updated_sched.replace(to_replace=r'.*Cena dostawy.*', value='dostepne', regex=True)
        updated_sched = updated_sched.replace(to_replace=r'.*bezpłatna od.*', value='niedostepne', regex=True)

        return updated_sched


    def get_available_schedule(self,):
        terminy = self.wait_until_visible(10, terminy_dostaw)
        terminy[0].click()
        popup = self.wait_until_visible(5, times_table_popup)

        schedule = self.dump_table_from_webpage(popup[0].get_attribute('innerHTML'))

        image = self.take_schedule_screenshot()
        image_file = 'api_schedule.png'
        with open(image_file, 'wb') as f:
            f.write(image)
        
        return self.change_schedule_table(schedule)


    def take_schedule_screenshot(self):
        popup = self.wait_until_visible(5, times_table_popup)

        return popup[0].screenshot_as_png


    def check_deliveries_within(self, schedule: pd.DataFrame, days: int) -> pd.DataFrame:
        possible_deliveries = [column for column in schedule.columns[1:] if
                            schedule[column].str.contains('dostepne').any()]
        possible_deliveries_dt = [datetime.strptime(delivery_date.split()[1] + '.2020', '%d.%m.%Y') for delivery_date in
                                possible_deliveries]
        deliveries_in_period = [delivery_date
                                for delivery_date in possible_deliveries_dt
                                if delivery_date.date() < (datetime.now() + timedelta(days=days)).date()
                                ]

        return deliveries_in_period
