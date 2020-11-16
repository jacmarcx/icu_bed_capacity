import os
import csv
import datetime
from bs4 import BeautifulSoup
from github import Github
import time
import requests
import tempfile
from datetime import datetime, timedelta
import pytz

# access Github repo
token = os.environ['GH_TOKEN']
g = Github(token)
repo = g.get_repo('jacmarcx/icu_bed_capacity')

# commit string
t = datetime.now(pytz.timezone('America/Winnipeg')).strftime('%Y-%m-%d--%H')
commit = 'hourly update: ' + str(t)


try:
    url = 'https://whiteboard.manitoba-ehealth.ca/whiteboard/icu'

    log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    # get headers
    headers = soup.find('thead', attrs={'class':'whiteboard responsive_thead'}).find_all('th')
    head_row = [i.get_text().lower() for i in headers]

    # get values
    hosps = soup.find('tbody', attrs={'class':'whiteboard responsive_tbody'}).find_all('tr')
    for h in hosps:    
        vals = [x.text for x in h.find_all('td')]      
        vals_file_exists = os.path.isfile('icu_beds.csv')

        with open('icu_beds.csv', 'a+', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',')
            if not vals_file_exists:
                csv_writer.writerow(['log_time'] + head_row)           
            csv_writer.writerow([log_time] + vals)
            
    log_file_exists = os.path.isfile('logs.csv')
    with open('logs.csv', 'a+', newline='') as g:
        csv_writer = csv.writer(g, delimiter=',')
        if not log_file_exists:
            csv_writer.writerow(['log_time','status'])
        csv_writer.writerow([log_time, 'successful scrape'])

    # send to repo
    with open('icu_beds.csv', 'r') as reader:
        data_vals = reader.read()
        repo.create_file('data/' + t + '.csv', commit, data_vals)
        
    with open('logs.csv', 'r') as reader:
        data_logs = reader.read()   
        repo.create_file('logs/' + t + '.csv', commit, data_logs)        

   
except:
    log_file_exists = os.path.isfile('logs.csv')
    with open('logs.csv', 'a+', newline='') as g:
        csv_writer = csv.writer(g, delimiter=',')
        if not log_file_exists:
            csv_writer.writerow(['log_time','status'])
        csv_writer.writerow([log_time, 'failed scrape'])
    # send to repo
    with open('logs.csv', 'r') as reader:
        data_logs = reader.read()    
        repo.create_file('logs/' + t + '.csv', commit,data_logs)

















































