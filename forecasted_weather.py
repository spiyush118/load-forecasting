import requests
import csv
import numpy as np
import os
from bs4 import BeautifulSoup
from pandas import DataFrame
url_fore = 'https://weather.com/en-IN/weather/tenday/l/New+Delhi+India+INXX0096:1:IN'
url_load = 'https://www.delhisldc.org/Loaddata.aspx?mode='
url_weather = 'https://www.wunderground.com/history/airport/VIDP/%d/%d/%d/DailyHistory.html'


def forecast_weather():
    resp = requests.get(url_fore)
    table=[]
    soup = BeautifulSoup(resp.text, 'lxml') # Yummy HTML soup

    attributes=["temp","humidity","description"]
    rows = soup.findAll("tr",{"class" : "clickable closed"} )
    for tr in rows:
        row=[]
        for attr in attributes :
            lis=tr.find("td",{"class" : attr})
            lis.find_all("span",{"class":""})
            for l in lis:
               row.append(lis.text)
        table.append(row)
    table=DataFrame(table,columns=attributes)
    table.to_csv("forecast_weather.csv",index=None)

def update_load(s_date):
    s_day,s_month,s_year=tuple(s_date.split("-"))
    s_day=int(s_day)
    s_month=int(s_month)
    s_year=int(s_year)
    now=datetime.datetime.now().date()
    year_range=[now.year]
    month_range = list(range(s_month,now.month+1))
    #day_range = list(range(1, 32)) # days, 1 to 31

    # months, Aug to Dec for 2017, and Jan for 2018
    day_range = {s_month: list(range(s_day,32)), now.month: list(range(s_day,now.day+1)) }
    day_range.update(dict.fromkeys(list(range(s_month+1,now.month)),list(range(1,32))))

    if not os.path.exists('SLDC_Data'):
                os.makedirs('SLDC_Data')

    for year in year_range:
            for month in month_range:
                    month_dir = 'SLDC_Data/%d/%02d/' %(year, month)
                    if not os.path.exists(month_dir): os.makedirs(month_dir)
                    try:
                            for day in day_range[month]:
                                    date = '%02d/%02d/%d' %(day, month, year)
                                    print('Scraping', date)
                                    resp = requests.get(url_load+date) # send a get request to the url, get response
                                    soup = BeautifulSoup(resp.text, 'lxml') # Yummy HTML soup
                                    table = soup.find('table', {'id':'ContentPlaceHolder3_DGGridAv'}) # get the table from html
                                    trs = table.findAll('tr') # extract all rows of the table
                                    if len(trs[1:])!=0: # no need to create csv file, if there's no data, for Aug month of 2017
                                            csv_filename = month_dir + '%s.csv' % date.replace('/', '-')
                                            if os.path.exists(csv_filename): os.remove(csv_filename) # remove the file it already exists, can result in data duplicacy
                                            with open(csv_filename, 'a') as f:
                                                    writer = csv.writer(f)
                                                    writer.writerow(['time', 'value'])
                                                    for tr in trs[1:]:
                                                            time, delhi = tr.findChildren('font')[:2]
                                                            writer.writerow([time.text, delhi.text])
                    except Exception as e:
                            print(e)

def update_weather(s_date):
    s_day,s_month,s_year=tuple(s_date.split("-"))
    s_day=int(s_day)
    s_month=int(s_month)
    s_year=int(s_year)
    now=datetime.datetime.now().date()
    year_range=[now.year]
    month_range = list(range(s_month,now.month+1))
    #day_range = list(range(1, 32)) # days, 1 to 31

    # months, Aug to Dec for 2017, and Jan for 2018
    day_range = {s_month: list(range(s_day,32)), now.month: list(range(s_day,now.day+1)) }
    day_range.update(dict.fromkeys(list(range(s_month+1,now.month)),list(range(1,32))))
    

    if not os.path.exists('Whether_Data'):
                os.makedirs('Whether_Data')



    for year in year_range:
            for month in month_range:
                    month_dir = 'Whether_Data/%d/%02d/' %(year, month)
                    if not os.path.exists(month_dir): os.makedirs(month_dir)
                    for day in day_range[month]:
                            try:
                                    date = '%02d/%02d/%d' %(day, month, year)
                                    print('Scraping', date)
                                    current_url = url_weather % (year, month, day)
                                    resp = requests.get(current_url) # send a get request to the url, get response
                                    soup = BeautifulSoup(resp.text, 'lxml') # Yummy HTML soup
                                    table = soup.find('table', {'id':'obsTable'}) # get the table from html
                                    trs = table.findAll('tr') # extract all rows of the table
                                    if len(trs[1:])!=0:
                                            csv_filename = month_dir + '%s.csv' % date.replace('/', '-')
                                            if os.path.exists(csv_filename): os.remove(csv_filename) # remove the file it already exists, can result in data duplicacy
                                            with open(csv_filename, 'a') as f:
                                                    writer = csv.writer(f)
                                                    columns = [th.text for th in trs[0].findChildren('th')]					
                                                    writer.writerow(columns)
                                                    for tr in trs[1:]:
                                                            row = []
                                                            tds = tr.findChildren('td')
                                                            for td in tds:
                                                                    span = td.findChildren('span', {'class':'wx-value'})
                                                                    if span:
                                                                            row.append(span[0].text.strip())
                                                                    else:
                                                                            row.append(td.text.strip())
                                                            assert len(row) == len(columns)
                                                            writer.writerow(row)
                            except Exception as e:
                                    print('Exception', e)
                                    print(date)
                                    print(current_url)



