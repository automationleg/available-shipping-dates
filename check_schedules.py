import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os
from browser import BasePage
from frisco_schedule import Frisco
from apimarket_schedule import Apimarket
import time
import requests


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

    # check schedule for apimarket
    api = Apimarket()
    api.get_page()
    api.enter_zip_code('05510')

    # login
    api.login(username, password)
    time.sleep(2)
    schedule = api.get_available_schedule()

    image = api.take_schedule_screenshot()
    print(schedule)
    api.quit()

    # notify external service
    available_dates = api.check_deliveries_within(schedule, days=10, occurences=3)
    # update images with schedules
    send_file_to_openhab(filename='api_schedule.png', hostname=notifip)


    # execute for frisco
    frisco = Frisco()
    frisco.get_page()
    frisco.login(username, password)

    # check reservation
    frisco.reservation()

    #send file
    send_file_to_openhab('frisco_schedule.png', notifip)

    frisco.quit()

    # send openhab notifications
    if notifip is not None:
        if available_dates:
            print('Available deliveries. Sending notification')
            requests.put(f'http://{notifip}:8080/rest/items/api/state', 'ON')
            requests.put(f'http://{notifip}:8080/rest/items/frisco/state', 'ON')
        else:
            requests.put(f'http://{notifip}:8080/rest/items/api/state', 'OFF')
            requests.put(f'http://{notifip}:8080/rest/items/frisco/state', 'OFF')



