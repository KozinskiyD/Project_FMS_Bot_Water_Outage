from http.client import responses

import requests
from bs4 import BeautifulSoup

url = 'http://93.92.65.26/aspx/Gorod.htm'
response = requests.get(url)
bs = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")

extracted_text = bs.get_text()
encoded_text = extracted_text.encode('utf-8', errors='replace')
decoded_text = encoded_text.decode('utf-8')

print(decoded_text)
"""
def check_water_outage():
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка HTTP-статуса
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск в конкретных HTML-элементах
        elements = soup.find_all(['div', 'p', 'article', 'section', 'body'])
        for elem in elements:
            text = elem.get_text(separator=' ', strip=True)
            if 'Центральный район' in text:
                print(text)

    except requests.exceptions.RequestException as e:
        print("Ошибка подключения:", e)
    except Exception as e:
        print("Ошибка:", e)

check_water_outage()
"""