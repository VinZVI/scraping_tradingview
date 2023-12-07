#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
from bs4 import BeautifulSoup
import datetime
import csv
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

    name_file = f"tradingview_{CUR_TIME}_posts.csv"

    with open(name_file, "w") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Имя",
                "Ссылка"
            )
        )

    idea_authors_data = []

    for page in range(1, 11):

        url = f"https://br.tradingview.com/ideas/page-{page}/"

        try:
            response = requests.get(url=url, params=PARAMS, headers=HEADERS)
            print(response.status_code)
        except Exception as e:
            print(e)

        # with open(f"result_page_{page}.html", "w", encoding="utf-8") as file:
        #     file.write(response.text)

        soup = BeautifulSoup(response.text, "lxml")

        try:
            post_items = soup.find_all("div", class_='tv-widget-idea js-userlink-popup-anchor')
        except Exception as e:
            print(e)

        for pi in post_items:
            post_data = pi.find_all("div")

            try:
                post_author = pi.find('a', class_='tv-card-user-info__main-wrap js-userlink-popup').text.strip()

                print(post_author)
            except Exception as e:
                print(e)

            try:
                post_author_link = pi.find('a', class_='tv-card-user-info__main-wrap js-userlink-popup')['href']
                link = f'https://br.tradingview.com{post_author_link}'
                print(link)
            except Exception as e:
                print(e)

            # try:
            #     count_boosts = pi.find('span', class_='tv-card-social-item__count').text.strip()
            #
            #     print(count_boosts)
            # except Exception as e:
            #     print(e)

            idea_authors_data.append((post_author, link))  # , count_boosts))

        print(f"Обработана {page}/500")
    idea_authors_data = set(idea_authors_data)
    idea_authors_data = list(idea_authors_data)
    # # sorted by count of boosts
    # idea_authors_data.sort(key=lambda elem: elem[2])

    with open(name_file, "w") as file:
        writer = csv.writer(file)

        for author in idea_authors_data:
            writer.writerow(
                (
                    author[0],
                    author[1]
                )

            )
    return name_file, idea_authors_data


def get_users_data(name_file, idea_authors_data):
    """
            :param name_file: str 'Name csv file with name user and link'
            :param idea_authors_data: list 'data name user and link'
            :return: exel file  with name use, link, subscribers, ideas, scripts
    """

    authors_data = []

    lines = len(idea_authors_data)

    # name_file_final = f"tradingview_{CUR_TIME}.csv"

    # with open(name_file_final, "w") as file:
    #     writer = csv.writer(file)
    #
    #     writer.writerow(
    #         (
    #             "Имя",
    #             "Ссылка",
    #             "Количество подписчиков",
    #             "Идей",
    #             "Скриптов"
    #         )
    #     )

    with open(name_file, "r") as file:
        idea_authors_data = file.readlines()
        idea_authors_data.reverse()
        print(idea_authors_data)
        lines = len(idea_authors_data) / 2

    count = 1

    for author in idea_authors_data:

        if author == '\n':
            continue

        author = author.split(',')
        print(author)

        # Get author's link
        url = author[1].strip()

        try:
            cur_time = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")

            params = {
                'from': f'u/{author[0]}/',
                'date': cur_time,
            }
            response = requests.get(url=url, params=params, headers=HEADERS)

            print(response.status_code)
            if response.status_code != 200:
                continue
        except Exception as e:
            print(e)

        # with open(f"result_page_{page}.html", "w", encoding="utf-8") as file:
        #     file.write(response.text)

        soup = BeautifulSoup(response.text, "lxml")

        try:
            user_data = soup.find_all('span', class_='tv-profile__social-item apply-common-tooltip')
        except Exception as e:
            print(e)

        try:
            subscribers = user_data[0].find_next().text.strip()
            print(subscribers)
        except Exception as e:
            print(e)

        try:
            ideas = user_data[2].find_next().text.strip()
            print(ideas)
        except Exception as e:
            print(e)

        try:
            scripts = user_data[3].find_next().text.strip()
            print(scripts)
        except Exception as e:
            print(e)

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
        print(f"Обработана {count}/{lines}")
        count += 1
        if count == 50:
            time.sleep(30)

    print(authors_data)
    authors_data.sort(key=lambda elem: int(elem[2]), reverse=True)

    get_new_xlfile(authors_data)

    # with open(name_file_final, "a") as file:
    #     writer = csv.writer(file)
    #
    #     for item in authors_data:
    #         writer.writerow(
    #             (
    #                 item['author_name'],
    #                 item['author_link'],
    #                 item['author_subscribers'],
    #                 item['author_ideas'],
    #                 item['author_scripts']
    #             )
    #         )


def get_new_xlfile(authors_data):
    """ Создаем новый файл"""
    wn = openpyxl.Workbook()
    # добавляем новый лист
    wn.create_sheet(title=CUR_TIME, index=0)
    # получаем лист, в который будем записывать
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
    name_file, idea_authors_data = get_data_posts_idea()
    # name_file = 'tradingview_2023_12_06-19_21_posts.csv'
    # idea_authors_data = []
    get_users_data(name_file, idea_authors_data)
    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")


if __name__ == '__main__':
    main()
