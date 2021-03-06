import requests
import re
from bs4 import BeautifulSoup
import html
from datetime import datetime
import jsonpickle
import os
from pathlib import Path

from typing import List


class Car:
    def __init__(self, make, full_name, date, img_url, page_url, download_link, description):
        self.page_url = page_url
        self.img_url = img_url
        self.date = date
        self.full_name = full_name
        self.make = make
        self.download_link = download_link
        self.description = description


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
        # _1ozXL is class of root node of a car cell
        cars_cells = soup.find_all('div', {'class': '_1ozXL'}) or []

        make_cars = []

        for cell in cars_cells:
            img_url = cell.find('img').get('src')

            s = cell.find('h2').text
            match = re.search(r'Posted (.+):\s*(.+)', s)
            date = match.group(1).replace('\xa0', ' ').replace(',', '')
            name = match.group(2)

            a = cell.find('a')
            download_link = url if a is None else a["href"] or url

            spans = set([x.text for x in cell.find_all('span')])
            spans = [html.unescape(x).replace('\xa0', ' ').strip() for x in spans]
            description = [x for x in spans
                           if not x.startswith('Posted')
                           and x != 'MORE INFO'
                           and x != name]
            description = [re.sub(r' +', ' ', x) for x in description]

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
                                 download_link=download_link,
                                 description=description))

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
        def filter_description():
            desc = car.description
            desc.sort()
            desc.reverse()

            desc_filtered = []
            for x in desc:
                bad = False
                for y in desc_filtered:
                    if x in y:
                        bad = True
                if not bad:
                    desc_filtered.append(x)

            return desc_filtered

        img = f'<img src="{car.img_url}" height="150"/>'
        html += f'<tr><td>{img}</td>'

        lines = [
            car.full_name,
            car.date.strftime("%d %b %Y"),
            '',
        ]
        lines.extend([x for x in filter_description() if x != '&'])
        lines.extend([
            f'<a href="{car.download_link}">Download</a>'
        ])

        html += f'<td><br>{"</br><br>".join(lines)}</br></td>'

        html += "</tr>"
    html += "</table></html>"

    html = BeautifulSoup(html, features="html.parser").prettify()

    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)


def open_report_in_browser():
    import webbrowser
    import os
    url = os.path.abspath('report.html')
    webbrowser.open_new_tab(url)


if __name__ == '__main__':
    dump()
    generate_html()
    open_report_in_browser()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
