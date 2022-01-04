from bs4 import BeautifulSoup as bs
import requests, re
import numpy as np
import pandas as pd

from googleapiclient.discovery import build
from google.oauth2 import service_account

'''
HOW TO GET HEADERS
Open dev tools and go to Network tab
Right-click on top page and select "Copy"
Select "Copy as cURL (bash)"
Paste into https://curlconverter.com/# and copy headers and params below
'''

site = 'https://artofproblemsolving.com/classroom/message-lookup'

headers = {
    'authority': 'artofproblemsolving.com',
    'cache-control': 'max-age=0',
    'authorization': 'Basic YWR2b2NhdGU6cGVyZmVjdGlvbi1UMg==',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_gcl_au=1.1.594114032.1633912015; _fbp=fb.1.1633912015174.29103382; _hjid=29152329-3fc4-4514-8cb0-d959ec7b292f; _ga_RVQHGWMEXD=GS1.1.1636407150.2.0.1636407193.0; _hjSessionUser_774800=eyJpZCI6IjdlYzFkNGU5LWU4Y2ItNTliYS05MmJiLTUyNmQ4NjQyZjFiNCIsImNyZWF0ZWQiOjE2MzcxNTU2OTg5NjEsImV4aXN0aW5nIjp0cnVlfQ==; _gaexp=GAX1.2.dxfxXNRDRY28Y3y4TyuTxQ.19048.0; timezone=eastern; _gid=GA1.2.1947076679.1641213676; _hjSession_774800=eyJpZCI6Ijk5MzM1ZTU3LWMzZjYtNGM2OC1iZTdlLTJiNmJlMGQ4MzAxZSIsImNyZWF0ZWQiOjE2NDEyMTM2NzY5MTJ9; _hjAbsoluteSessionInProgress=1; _clck=19m46uv|1|ext|0; dash_init_time=1641213792; aopssid=HyOMqArubTAw16412138044484rcdnxyNFNmYl; aopsuid=595181; auid=595181; alogin=s3mei8; grid_init_time=1641221556; crypt_init_time=1641222715; xo_init_time=1641224548; _hjIncludedInSessionSample=1; _uetsid=719555506c9211eca3d481caf525fa95; _uetvid=effda9d02a2911ecadfef98d973e40b0; _ga_NVWC1BELMR=GS1.1.1641219343.330.1.1641226661.60; _ga=GA1.2.1884021289.1633912015; _clsk=ca6z2f|1641226661982|76|1|d.clarity.ms/collect',
}


def get_username_and_class_id():
  '''Retrieves username and class ID from Google sheet.'''

  SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
  SERVICE_ACCOUNT_FILE = 'key.json'

  credentials = None
  credentials = service_account.Credentials.from_service_account_file(
          SERVICE_ACCOUNT_FILE, scopes=SCOPES)

  SPREADSHEET_ID = '1rXesuUIA0rBsPdQKAeKcnZ06KaTmprNjgJNvzywprjM'

  service = build('sheets', 'v4', credentials=credentials)

  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1:B2").execute()

  values = result.get('values', [])

  return values


def get_html(site, headers, assistant, id):
  '''
  Returns text and url paramenters (username, room-id) (dict)
  site -> the url (str)
  headers -> needed to log in to site (dict)
  assistant -> assistant username (str)
  id -> class ID (str)
  '''

  params = (
    ('user', assistant),
    ('room-id', id),
  )

  response = requests.get(site, headers=headers, params=params)
  soup = bs(response.text, 'lxml')
  site_text = soup.find(id='main-column')

  return {'content': site_text, 'params': params}


def clean_html(scrape_info):
  params = scrape_info['params']
  html_content = scrape_info['content']

  chat_data = [re.sub('[\t\n\[\]]'," ", message) for message in html_content.stripped_strings]

  site_text = []
  for content in chat_data:
    if params[0][1] in content and "Messages from" not in content:
      split_content = content.split()
      message = " ".join(split_content[5:])
      message_info = split_content[0:5]
      message_info.append(message)
      site_text.append(message_info)

  pd_array = pd.DataFrame(site_text, columns = ['Date','Time','Sender', 'Symbol', 'Recipient', 'Message'])
  new_df = pd_array.drop(columns=["Symbol"], axis=1)

  return new_df

assistant_data = get_username_and_class_id()
username = assistant_data[1][0]
class_id = assistant_data[1][1]

site_scrape = get_html(site, headers, username, class_id)
cleaned_content = clean_html(site_scrape)
print(cleaned_content)


# print(chat_content.prettify())

# One way to remove \n and \t
# array = [message.replace("\n", "") for message in chat_content.stripped_strings]
# new_array = [content.replace("\t", "") for content in array]

'''
Try regex
# re.sub(pattern, repl, string, count=0, flags=0)
'''
# chat_data = [re.sub('[\t\n\[\]]'," ", message) for message in chat_content.stripped_strings]
# date = chat_data[1]
# chat_data_reduced = [message for message in chat_data if message[0] == "["]

# print(chat_data[:20])
# print(date)
# print()
# print(chat_data_reduced[:10])

# print(pd_array)
# print(new_df)
# new_df = new_df.convert_dtypes()
# pd.to_datetime(new_df)
# print(new_df.dtypes)

# print(chat_data[3].split())
# test_list = chat_data[3].split()[5:]
# print(" ".join(test_list))





  