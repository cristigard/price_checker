from bs4 import BeautifulSoup
import datetime
import requests
import mariadb
import sys
import os
import smtplib

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD =os.environ.get('EMAIL_PASS')

#current time
date=datetime.datetime.now()

#scrap price
source = requests.get('https://www.cursbnr.ro/').text
soup=BeautifulSoup(source,'lxml')
euro = soup.find('div', class_='currency-value').text
price_euro=euro[10:16]

#connct to DB
try:
    conn = mariadb.connect(
        user="price",
        password="qwerty",
        host="192.168.72.128",
        port=3306,
        database="price"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cursor = conn.cursor() # Get Cursor
conn.autocommit = True # Enable Auto-Commit

# insert information
try:
    cursor.execute("INSERT INTO price_values (pv_price_current,pv_datetime) VALUES (?, ?)",(price_euro, date))
except mariadb.Error as e:
    print(f"Error occurs on interact with database: {e}")

# retrieving information Max price
max_price = ''
try:
    cursor.execute(
        'SELECT pv_price_current,pv_datetime FROM price_values WHERE pv_price_current = (SELECT Max(pv_price_current) FROM price_values )LIMIT 1')
    for pv_price_current, pv_datetime in cursor:
        max_price += "Max price: " + str(pv_price_current) + " at " + str(pv_datetime)
except mariadb.Error as e:
    print(f"Error: {e}")

# retrieving information Min price
min_price = ''
try:
    cursor.execute(
        'SELECT pv_price_current,pv_datetime FROM price_values WHERE pv_price_current = (SELECT Min(pv_price_current) FROM price_values) LIMIT 1')
    for pv_price_current, pv_datetime in cursor:
        min_price += "Min price: " + str(pv_price_current) + " at " + str(pv_datetime)
except mariadb.Error as e:
    print(f"Error: {e}")

# Close connection to DB
conn.close()

# Send mail
with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    subject = 'Price different!'
    body = f"{max_price}\n{min_price}"
    msg = f'Subject: {subject}\n\n{body}'
    smtp.sendmail(EMAIL_ADDRESS, 'gc...@gmail.com', msg)
    print("done")
