import gspread
import requests
import json
import urllib.parse
from googleapiclient.discovery import build
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def load_googlesheets_to_json(filename):
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    # Указываем путь к JSON
    gc = gspread.service_account(filename='smm-planner-384116-1f650199dcd3.json')
    #Открываем тестовую таблицу
    sh = gc.open("Test")
    worksheet = sh.worksheet("Class Data")
    #Выводим значение ячейки A1
    list_of_lists = worksheet.get_all_values()
    data = []
    for index, row in enumerate(list_of_lists[1::], 2):
        not_good = 0
        for i in row:
            if not i:
                not_good += 1
        if not_good > 1:
            worksheet.update_cell(index, 5, 'Не все значения введены')
            continue
        doc_url = row[0]
        text = []
        doc_url = urllib.parse.urlparse(row[0])
        DOCUMENT_ID = doc_url.path.split('/')[3]
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=DOCUMENT_ID).execute().get('body').get('content')
        text = []
        for paragraph in document:
            if 'startIndex' in paragraph:
                text.append(paragraph['paragraph']['elements'][0]['textRun']['content'].replace('\n', ''))
        img_url = row[1]
        img_response = requests.get(img_url)
        img_response.raise_for_status()
        with open(f'images/img_{index}.jpg', 'wb+') as file:
            file.write(img_response.content)
        text = '\n'.join(text)
        text.replace('-', '–')
        text = ' '.join(text.split())
        s = text.split('"')
        for i in range(1, len(s), 2):
            s[i] = chr(171) + s[i] + chr(187)
        text = ''.join(s)
        s = text.split("'")
        for i in range(1, len(s), 2):
            s[i] = chr(171) + s[i] + chr(187)
        text = ''.join(s)
        print(text)
        data.append({
            'text': text,
            'img': f'images/img_{index}.jpg',
            'date': row[2].split()[0],
            'time': row[2].split()[1],
            'platform': row[3]
        })
        if row[4] != "Опубликовано":
            worksheet.update_cell(index, 5, 'Добавлено в базу данных')
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def change_status(index, status):
    gc = gspread.service_account(filename='smm-planner-384116-1f650199dcd3.json')
    sh = gc.open("Test")
    worksheet = sh.worksheet("Class Data")
    worksheet.update_cell(index+2, 5, status)


def get_status(index):
    gc = gspread.service_account(filename='smm-planner-384116-1f650199dcd3.json')
    sh = gc.open("Test")
    worksheet = sh.worksheet("Class Data")
    rows = worksheet.get_all_values()
    return rows[index+1][4]
