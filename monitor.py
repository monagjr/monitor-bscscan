import subprocess
from playsound import playsound
import requests
from bs4 import BeautifulSoup
import urllib.parse
import hashlib
import pickle
from os import path
import sys
import time
from datetime import datetime

# load input urls to monitor
if not path.exists('urls.txt'):
    sys.exit('urls.txt file can not be found')

input_urls = []

with open('urls.txt', 'r') as f:
    input_urls = [u.strip() for u in f.readlines()]

if not input_urls:
    sys.exit('urls.txt is empty')

monitored_urls = {}

# load monitored urls state
if path.exists('state.data'):
    with open('state.data', 'rb') as f:
            monitored_urls = pickle.load(f)

while True:
    for url in input_urls:
        now = datetime.now()
        print('%s Checking %s ...' % (now.strftime("%d/%m/%Y %H:%M:%S"),url))
        
        token = ''
        response = requests.get(url)
        content = response.content.decode('utf-8')

        res = BeautifulSoup(content, 'html.parser')
        topItemUrl = res.findAll('a', attrs={'class': 'hash-tag'})[0]
        # check if it is failed transaction
        isFailed = True if topItemUrl.previous_sibling else False
        topItemUrl = topItemUrl['href']
        topItemUrl = urllib.parse.urljoin(url, topItemUrl)
        monitored_url_key = hashlib.md5(url.encode('utf-16')).hexdigest()
        if (monitored_url_key not in monitored_urls) or ( monitored_urls[monitored_url_key] != topItemUrl):
            # alert if difference only not new page
            if monitored_url_key in monitored_urls:
                print ('Change Detected!')
                # follow if not failed transaction only
                if not isFailed:
                    response = requests.get(topItemUrl)
                    content = response.content.decode('utf-8')
                    res = BeautifulSoup(content, 'html.parser')
                    last_transcation_action_url = res.findAll('a', attrs={'class': 'd-inline-block'})[-1]
                    token = last_transcation_action_url.split('/')[-1]
                    # copy token to clipboard
                    subprocess.run(['clip.exe'], input=token.encode('utf-16'), check=True)
                    print ('Token %s copied to Clipboard' % token)
                print ('Failed Transaction')
                # play alert sound
                playsound('alert.mp3')
            else:
                print ('New Url. First Check!')
            monitored_urls[monitored_url_key] = topItemUrl
            with open('state.data', 'wb') as f:
               pickle.dump(monitored_urls, f, pickle.HIGHEST_PROTOCOL)
        else:
            print ('No Change!')
        time.sleep(1/(len(input_urls)+1))
   


