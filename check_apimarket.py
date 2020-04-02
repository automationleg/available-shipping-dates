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


login_header = (By.XPATH, '//h3[text()="Masz już konto?"]')
zip_popup_close = (By.XPATH, '//div[contains(@class, "fancybox-overlay")]//a[@title="Close"]')
submit_zip_code = (By.XPATH, '//div[contains(@class, "fancybox-overlay")]//button[@type="submit"]')
terminy_dostaw = (By.CLASS_NAME, 'ard-top-time-slots')
times_table_popup = (By.CLASS_NAME, 'time-slots-popup')
next_days = (By.CLASS_NAME, 'ts-next')


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


def initialize_browser(remote):
    if remote:
        return webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=set_chrome_options())
    else:
        return webdriver.Chrome(options=set_chrome_options())


def wait_until_visible(webdriver, wait_time, *locator, error_message=''):
    return WebDriverWait(webdriver, wait_time).until(
        EC.visibility_of_all_elements_located(*locator),
        message=f'{error_message}\n'
        f'Details: Element with the following locator "{locator}" was not displayed within {wait_time} seconds'
    )


def login(username, password):
    login = browser.find_element_by_class_name('login')
    login.click()

    # wait for login form
    wait_until_visible(browser, 10, login_header)

    email_field = browser.find_element_by_id('email').send_keys(username)
    pass_field = browser.find_element_by_id('passwd').send_keys(password)
    time.sleep(1)
    browser.find_element_by_id('SubmitLogin').click()


def enter_zip_code(zipcode):
    # close any popup
    browser.find_element_by_xpath('//input[@name="post_code"]').send_keys('05510')
    browser.find_element(*submit_zip_code).click()
    # browser.find_element(*zip_popup_close).click()
    time.sleep(3)


def change_schedule_table(df):
    updated_sched = df.copy(deep=True)
    updated_sched = updated_sched.replace(to_replace=r'.*Cena dostawy.*', value='niedostepne', regex=True)
    updated_sched = updated_sched.replace(to_replace=r'.*bezpłatna od.*', value='dostepne', regex=True)

    return updated_sched


def get_available_schedule():
    terminy = wait_until_visible(browser, 10, terminy_dostaw)
    terminy[0].click()
    popup = wait_until_visible(browser, 5, times_table_popup)

    schedule = dump_table_from_webpage(popup[0].get_attribute('innerHTML'))
    return change_schedule_table(schedule)


def take_schedule_screenshot():
    popup = wait_until_visible(browser, 5, times_table_popup)

    return popup[0].screenshot_as_png


def check_deliveries_within(schedule: pd.DataFrame, days: int) -> pd.DataFrame:
    possible_deliveries = [column for column in schedule.columns[1:] if
                           schedule[column].str.contains('dostepne').any()]
    possible_deliveries_dt = [datetime.strptime(delivery_date.split()[1] + '.2020', '%d.%m.%Y') for delivery_date in
                              possible_deliveries]
    deliveries_in_period = [delivery_date
                            for delivery_date in possible_deliveries_dt
                            if delivery_date.date() < (datetime.now() + timedelta(days=days)).date()
                            ]

    return deliveries_in_period


def dump_table_from_webpage(page_source):
    """
    Dumps whole table displayed on webpage into a pandas DataFrame
    :return: table as DataFrame object
    """

    page_soup = BeautifulSoup(page_source, 'lxml')

    assert page_soup, 'Was not able to dump page source data!'

    first_table = page_soup.find_all('table')[0]

    table_df = pd.read_html(str(first_table))

    # pandas data frame representation of table
    return table_df[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("available-schedules")
    parser.add_argument("-u", "--user", type=str, help="Login User Name")
    parser.add_argument("-p", "--password", type=str, help="Login Password")
    parser.add_argument("-r", "--remote", default=False, action="store_true", help="Webdriver Remote. default=False")
    parser.add_argument("-ip", "--ipaddress", type=str, help="IP address of service to notify")

    args = parser.parse_args()

    pd.options.display.width = 0
    browser = initialize_browser(remote=args.remote)

    browser.get('https://apimarket.pl/')
    time.sleep(2)
    enter_zip_code('05510')

    # login
    login(args.user, args.password)
    time.sleep(2)
    schedule = get_available_schedule()

    image = take_schedule_screenshot()
    with open('api_schedule.png', 'wb') as f:
        f.write(image)

    print(schedule)

    # notify external service
    available_dates = check_deliveries_within(schedule, days=65)
    print(available_dates)
    print(hasattr(args, 'ip'))
    if hasattr(args, 'ip'):
        if available_dates:
            print('Available deliveries. Sending notificatoin')
            requests.post(f'http://{args.ip}:8080/rest/items/api/state', 'ON')
        else:
            requests.post(f'http://{args.ip}:8080/rest/items/api/state', 'OFF')

    browser.quit()

