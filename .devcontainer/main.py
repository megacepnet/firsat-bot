import cloudscraper
from bs4 import BeautifulSoup
import sqlite3
import requests
import time

TOKEN="BOT_TOKEN"
CHAT_ID="CHAT_ID"

scraper=cloudscraper.create_scraper()

db=sqlite3.connect("products.db")
cursor=db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
link TEXT PRIMARY KEY,
name TEXT,
price REAL
)
""")

db.commit()

def temizle(price):

    price=price.replace("TL","").replace(".","").replace(",",".")
    price="".join(c for c in price if c.isdigit() or c==".")

    try:
        return float(price)
    except:
        return 0

def telegram(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,data={
    "chat_id":CHAT_ID,
    "text":msg,
    "parse_mode":"HTML"
})

def indirim_kontrol(name,price,link):

    cursor.execute("SELECT price FROM products WHERE link=?",(link,))
    row=cursor.fetchone()

    if row is None:

        cursor.execute(
        "INSERT INTO products VALUES(?,?,?)",
        (link,name,price)
        )

        db.commit()

    else:

        old=row[0]

        if old>0:

            discount=((old-price)/old)*100

            if discount>=25:

                msg=f"""
🔥 FIRSAT

{name}

💰 Eski {old:.2f} TL
💸 Yeni {price:.2f} TL

📉 %{discount:.0f} indirim

{link}
"""

                telegram(msg)

        cursor.execute(
        "UPDATE products SET price=? WHERE link=?",
        (price,link)
        )

        db.commit()

def hepsiburada():

    url="https://www.hepsiburada.com/magaza/hepsiburada?kategori=371965"

    r=scraper.get(url)
    soup=BeautifulSoup(r.text,"html.parser")

    items=soup.find_all("li",class_="productListContent-item")

    for i in items:

        try:

            name=i.find("h3").text.strip()

            price=i.find(
            "div",
            {"data-test-id":"price-current-price"}
            ).text

            price=temizle(price)

            link="https://www.hepsiburada.com"+i.find("a")["href"]

            indirim_kontrol(name,price,link)

        except:
            pass

def trendyol():

    url="https://www.trendyol.com/sr?q=teknoloji"

    r=scraper.get(url)
    soup=BeautifulSoup(r.text,"html.parser")

    items=soup.find_all("div",class_="p-card-wrppr")

    for i in items:

        try:

            name=i.find("span",class_="prdct-desc-cntnr-name").text

            price=i.find("div",class_="prc-box-dscntd").text

            price=temizle(price)

            link="https://www.trendyol.com"+i.find("a")["href"]

            indirim_kontrol(name,price,link)

        except:
            pass

print("ULTRA BOT START")

while True:

    try:

        hepsiburada()
        trendyol()

    except Exception as e:

        print(e)

    time.sleep(300)
