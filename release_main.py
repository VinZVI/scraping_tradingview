#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Парсинг данных любой сложности Python
Мой профиль на Kwork: https://kwork.ru/user/vinilzm
Мой профиль на Github: https://github.com/VinZVI
"""

import time
import requests
from bs4 import BeautifulSoup
import datetime
import openpyxl

HEADERS = {
    'Pragma': 'no-cache',
    'Origin': 'https://br.tradingview.com',
    'Accept-Language': 'pt,en;q=0.9',
    'Sec-WebSocket-Key': 'Bln8g2vYGTJsWMThPAppaQ==',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.686 Safari/537.36',
    'Upgrade': 'websocket',
    'Cache-Control': 'no-cache',
    'Connection': 'Upgrade',
    'Sec-WebSocket-Version': '13',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
}

CUR_TIME = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")

PARAMS = {
    'from': 'ideas/',
    'date': CUR_TIME,
}


def get_data_posts_idea():
    """
    Get information about users from their posts with ideas  https://br.tradingview.com/ideas
    :return:
    """

    idea_authors_data = []

    page = int(input('Введите число страниц для парсинга от 1 до 500: ')) + 1

    for page in range(1, page):

        url = f"https://br.tradingview.com/ideas/page-{page}/"

        try:
            response = requests.get(url=url, params=PARAMS, headers=HEADERS)
            response.raise_for_status()
            print('status code: ', response.status_code)

        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except requests.ConnectionError:
            print(f"Connection error occurred for URL {url}")

        soup = BeautifulSoup(response.text, "lxml")

        try:
            post_items = soup.find_all("div", class_='tv-widget-idea js-userlink-popup-anchor')
        except Exception as e:
            print(e)

        for pi in post_items:

            try:
                post_author = pi.find('a', class_='tv-card-user-info__main-wrap js-userlink-popup').text.strip()

                print('post author: ', post_author)
            except Exception as e:
                print(e)

            try:
                post_author_link = pi.find('a', class_='tv-card-user-info__main-wrap js-userlink-popup')['href']
                link = f'https://br.tradingview.com{post_author_link}'
                print('link: ', link)
            except Exception as e:
                print(e)

            idea_authors_data.append((post_author, link))

        print(f"Обработана {page}/500")
    idea_authors_data = set(idea_authors_data)
    idea_authors_data = list(idea_authors_data)

    return idea_authors_data


def get_users_data(idea_authors_data):
    """
    :param name_file: str 'Name csv file with name user and link'
    :param idea_authors_data: list 'data name user and link'
    :return: exel file  with name use, link, subscribers, ideas, scripts
    """
    authors_data = []

    lines = len(idea_authors_data)

    count = 1

    for author in idea_authors_data:

        # Get author's link
        url = author[1]
        print('url: ', url)
        try:
            cur_time = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")

            params = {
                'from': f'u/{author[0]}/',
                'date': cur_time,
            }
            response = requests.get(url=url, params=params, headers=HEADERS)

            print('status code: ', response.status_code)
            response.raise_for_status()

        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            continue

        except requests.ConnectionError:
            print(f"Connection error occurred for URL {url}")

        soup = BeautifulSoup(response.text, "lxml")

        try:
            user_data = soup.find_all('span', class_='tv-profile__social-item apply-common-tooltip')
        except Exception as e:
            print(e)
            user_data = 'Данные пользователя не найдены'

        try:
            subscribers = user_data[0].find_next().text.strip()
            print('subscribers: ', subscribers)
        except Exception as e:
            print(e)
            subscribers = 'Число "подписчиков" не найдено, возможно изменение разметки'

        try:
            ideas = user_data[2].find_next().text.strip()
            print('ideas: ', ideas)
        except Exception as e:
            print(e)
            ideas = 'Число "идей" не найдено, возможно изменение разметки'

        try:
            scripts = user_data[3].find_next().text.strip()
            print('scripts: ', scripts)
        except Exception as e:
            print(e)
            scripts = 'Число "скриптов" не найдено, возможно изменение разметки'

        authors_data.append(
            [
                author[0],
                author[1],
                subscribers,
                ideas,
                scripts
            ]
        )
        time.sleep(3)
        print(f"Обработана {count}/{lines}\n")
        count += 1
        if count == 50:
            time.sleep(30)

    authors_data.sort(key=lambda elem: int(elem[2]), reverse=True)

    get_new_xlfile(authors_data)


def get_new_xlfile(authors_data):
    """ Get new file excel"""
    wn = openpyxl.Workbook()

    wn.create_sheet(title=CUR_TIME, index=0)

    new_sheet = wn[CUR_TIME]

    name_colum = (
        "Имя",
        "Ссылка",
        "Количество подписчиков",
        "Идей",
        "Скриптов"
    )

    new_sheet.append(name_colum)

    for item in authors_data:
        new_sheet.append(item)

    wn.save(f'tradingview_{CUR_TIME}.xlsx')


def main():
    start_time = time.time()
    idea_authors_data = get_data_posts_idea()
    get_users_data(idea_authors_data)
    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")


if __name__ == '__main__':
    main()
