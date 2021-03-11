# What is it

This tool parses all cars from https://assettoland.wixsite.com/assettoland/cars and sorts it by upload date.

# Why

There is no ability on assettoland to view all cars sorted by upload date.

# How it works

1) It parses every car make page and exports parsed data to folder **data**.
2) Reads dumped data and generates **report.html** - list of all cars sorted by upload date.

# How to use

#### Download [last generated report](/report.html) and open it using your browser.

#### Parse site and generate up-to-date report by yourself:

1) Clone repo
1) Run `pip3 install -r requirements.txt`
1) Run `python3 main.py`
1) Open generated `report.html` using your browser
