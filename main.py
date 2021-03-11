# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import jsonpickle
import os
from pathlib import Path

from typing import List


class Car:
    def __init__(self, make, full_name, date, img_url, page_url, download_link):
        self.page_url = page_url
        self.img_url = img_url
        self.date = date
        self.full_name = full_name
        self.make = make
        self.download_link = download_link

    @property
    def description(self):
        date_str = self.date.strftime("%d %b %Y")
        return f'{date_str}: {self.full_name} {self.page_url}'


def dump():
    url = 'https://assettoland.wixsite.com/assettoland/cars'
    text = requests.get(url).text
    # with open('test.html', 'w', encoding='utf-8') as output_file:
    #     output_file.write(text)

    matches = re.findall(r'data-testid="gallery-item-click-action-link" href="(.+?)"', text, flags=re.MULTILINE)
    print(matches)

    cars: list[Car] = []

    for idx, url in enumerate(matches):
        make = url.split('/')[-1]
        print(f"Parsing {make} ({idx + 1}/{len(matches)})")

        text = requests.get(url).text

        soup = BeautifulSoup(text, features="html.parser")
        cars_cells = soup.find_all('div', {'class': 'bDfMI'}) or []

        make_cars = []

        for cell in cars_cells:
            img_url = cell.find('img').get('src')

            s = cell.find('h2').text
            match = re.search(r'Posted (.+):\s*(.+)', s)
            date = match.group(1).replace('\xa0', ' ').replace(',', '')
            name = match.group(2)

            a = cell.find('a')
            download_link = url if a is None else a["href"] or url

            # 'Sep 05, 2020'
            try:
                date = datetime.strptime(date, '%b %d %Y')
            except ValueError as e:
                print(name, e)
                date = None

            make_cars.append(Car(make=make,
                                 full_name=name,
                                 date=date,
                                 img_url=img_url,
                                 page_url=url,
                                 download_link=download_link))

        cars += make_cars

        print(f'Parsed {len(make_cars)} cars\n')

        file_name = f'data/{make}'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w', encoding='utf-8') as f:
            json = jsonpickle.encode(make_cars)
            f.write(json)


def read_dumped_cars():
    cars: List[Car] = []

    for file_name in Path('data').glob('*'):
        with open(file_name, 'r', encoding='utf-8') as f:
            make_cars = jsonpickle.decode(f.read())
            cars += make_cars

    cars = [x for x in cars if x.date is not None]
    cars.sort(key=lambda x: x.date)

    for x in cars:
        x.img_url = x.img_url.split('/v1/')[0]

    return cars


def print_sorted():
    for car in read_dumped_cars():
        print(car.description)


def generate_html():
    cars = read_dumped_cars().__reversed__()

    html = f'''<html>
    <style>
    table, th, td {{
      border: 0px solid black;
      border-collapse: separate; /* allow spacing between cell borders */
      border-spacing: 0 5px; /* NOTE: syntax is <horizontal value> <vertical value> */
    }}
    
    table.center {{
      margin-left: auto; 
      margin-right: auto;
    }}

    td {{
       padding-left: 20px;
    }}

    tr {{
        padding-top: 10px;
    }}
    </style>
    <table class="center">
    <tr><th>{"</th><th>".join(['', ''])}</th></tr>'''
    for car in cars:
        img = f'<img src="{car.img_url}" height="150"/>'
        html += f'<tr><td>{img}</td>'

        lines = [car.full_name,
                 car.date.strftime("%d %b %Y"),
                 f'<a href="{car.download_link}">Download</a>']

        html += f'<td><br>{"</br><br>".join(lines)}</br></td>'

        html += "</tr>"
    html += "</table></html>"

    html = BeautifulSoup(html, features="html.parser").prettify()

    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    # dump()
    # print_sorted()
    generate_html()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
