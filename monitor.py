import subprocess
from playsound import playsound, PlaysoundException
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

input_proxies = []
if path.exists('proxies.txt'):
    with open('proxies.txt', 'r') as f:
        input_proxies = [u.strip() for u in f.readlines()]

monitored_urls = {}

# load monitored urls state
if path.exists('state.data'):
    with open('state.data', 'rb') as f:
            monitored_urls = pickle.load(f)

proxies = None
input_proxies_index = -1
while True:
    for url in input_urls:
        now = datetime.now()
        print('%s Checking %s ...' % (now.strftime("%d/%m/%Y %H:%M:%S"),url))
        
        token = ''
        response = requests.get(url, proxies=proxies)
        content = response.content.decode('utf-8')

        res = BeautifulSoup(content, 'html.parser')
        listUrls = res.findAll('a', attrs={'class': 'hash-tag'})
        if not len(listUrls):
            # print(content)
            if len(input_proxies):
                input_proxies_index = 0 if input_proxies_index > len(input_proxies) else input_proxies_index+1
                proxyIP = input_proxies[input_proxies_index]
            
                proxies = {
                  'http': proxyIP ,
                  'https': proxyIP,
                }
                print('Switch to Proxy ', proxyIP)
            continue
        topItemUrl = listUrls[0]
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
                    response = requests.get(topItemUrl, proxies=proxies)
                    content = response.content.decode('utf-8')
                    res = BeautifulSoup(content, 'html.parser')
                    last_transcation_action_url = res.findAll('a', attrs={'class': 'd-inline-block'})[-1]['href']
                    token = last_transcation_action_url.split('/')[-1]
                    # copy token to clipboard
                    subprocess.run(['clip.exe'], input=token.encode('utf-16'), check=True)
                    print ('Token %s copied to Clipboard' % token)
                else:
                    print ('Failed Transaction')
                # play alert sound
                try:
                    playsound('alert.mp3')
                except PlaysoundException:
                    print('Can not play sound! Check your soundcard')
            else:
                print ('New Url. First Check!')
            monitored_urls[monitored_url_key] = topItemUrl
            with open('state.data', 'wb') as f:
               pickle.dump(monitored_urls, f, pickle.HIGHEST_PROTOCOL)
        else:
            print ('No Change!')
        time.sleep(1/(len(input_urls)+1))
   


