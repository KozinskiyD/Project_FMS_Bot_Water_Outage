import requests
from bs4 import BeautifulSoup

url = 'http://005красноярск.рф/'

def check_water_outage():
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Проверка HTTP-статуса
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск в конкретных HTML-элементах
        elements = soup.find_all(['div', 'p', 'article', 'section'])
        for elem in elements:
            text = elem.get_text(separator=' ', strip=True)
            if ('Центральный район' in text):
                print(text)

    except requests.exceptions.RequestException as e:
        print("Ошибка подключения:", e)
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    check_water_outage()