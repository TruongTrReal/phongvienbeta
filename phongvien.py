import requests
# download and install requests with: pip install requests
from bs4 import BeautifulSoup
import asyncio
import os
import time
from dotenv import load_dotenv
# install python-dotenv with: pip install python-dotenv

from telegram import Bot
# install python-telegram-bot with: pip install python-telegram-bot

from telegram.ext import Updater
import openai
# install openai with: pip install openai

from datetime import datetime
# install datetime with: pip install datetime

import unidecode
# install unidecode with: pip install unidecode

from selenium import webdriver
# install selenium with: pip install selenium

from webdriver_manager.chrome import ChromeDriverManager
# install webdriver-manager with: pip install webdriver-manager
from selenium.webdriver.chrome.options import Options
#




# Set up the OpenAI API client
openai.api_key = "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"

load_dotenv()

TELEGRAM_API_KEY = ('6260954011:AAFiV-8H94nFg1PgTUEU1VtPELPjqc0bn3M')
TELEGRAM_CHANNEL_NAME = ('@tintaichinhbeta')
SCRAPING_INTERVAL_SECONDS = 5

# Link các mặt báo
url_newspaper = [
    # Báo cafef
    # 'https://cafef.vn/thi-truong-chung-khoan.chn',
    # 'https://cafef.vn/bat-dong-san.chn',
    # 'https://cafef.vn/doanh-nghiep.chn',
    # 'https://cafef.vn/tai-chinh-ngan-hang.chn',

    # # # Báo vietstock
    'https://vietstock.vn/chu-de/1-2/moi-cap-nhat.htm',

    # # # Báo lao động
    # 'https://laodong.vn/thi-truong',
    # 'https://laodong.vn/tien-te-dau-tu',
    # 'https://laodong.vn/doanh-nghiep-doanh-nhan',

    # # # Báo Tuổi trẻ
    # 'https://tuoitre.vn/kinh-doanh/dau-tu.htm',
    # 'https://tuoitre.vn/kinh-doanh/tai-chinh.htm',
    # 'https://tuoitre.vn/kinh-doanh/doanh-nghiep.htm',

    # # # Báo VnExpress
    # 'https://vnexpress.net/kinh-doanh/vi-mo',
    # 'https://vnexpress.net/kinh-doanh/quoc-te',
    # 'https://vnexpress.net/kinh-doanh/doanh-nghiep',
    # 'https://vnexpress.net/kinh-doanh/chung-khoan',
    # 'https://vnexpress.net/kinh-doanh/bat-dong-san',

    # # # BÁO VTV
    # 'https://vtv.vn/kinh-te.htm',

    # # # Báo Chính phủ
    # 'https://chinhphu.vn/tin-noi-bat-68258',



]

bot = Bot(TELEGRAM_API_KEY)
updater = Updater(bot=bot, update_queue=10)


sent_link = []
def delete_oldest_link():
    if len(sent_link) > 50:
        del sent_link[0]


# Define a function to summarize news articles
def summarize_news(url):
    # Get the HTML content of the article
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract the article text
    article_text = ''
    for paragraph in soup.find_all('p'):
        article_text += paragraph.text + '\n'
    # Use the OpenAI GPT API to summarize the article
    summary = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Tóm tắt bài báo này ngắn gọn trong khoảng 700 từ bằng tiếng Việt:\n{article_text}",
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5
    )
    # Extract the summary and metadata from the API response
    summary_text = summary.choices[0].text.strip()
    print('summarizing news')
    # Return the summary and metadata as a dictionary
    return summary_text


def get_headless_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

async def getnew(url):
    for _ in range(5):
        try:
            url_to_scrape = url
            response = requests.get(url_to_scrape, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # xử lí link báo cafef
            if url_to_scrape in ['https://cafef.vn/thi-truong-chung-khoan.chn','https://cafef.vn/bat-dong-san.chn','https://cafef.vn/doanh-nghiep.chn','https://cafef.vn/tai-chinh-ngan-hang.chn'] :
                driver = get_headless_chrome_driver()
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')                
                new_list = soup.find('div', ['class', 'tlitem box-category-item'])
                headline = new_list.find('h3')
                link = 'https://cafef.vn' + headline.find('a')['href']
                
                driver.quit()


            # xử lí link báo vietstock
            if url_to_scrape in ['https://vietstock.vn/chu-de/1-2/moi-cap-nhat.htm']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'single_post_text head-h'])
                headline = new_list.find('h4')
                link = 'https://vietstock.vn' + headline.find('a')['href']
                driver.quit()

            # xử lý link báo lao động
            if url_to_scrape in ['https://laodong.vn/doanh-nghiep-doanh-nhan','https://laodong.vn/thi-truong','https://laodong.vn/tien-te-dau-tu']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'p-lst-articles'])
                headline = new_list.find('div', ['class', 'pr'])
                link =  headline.find('a')['href']
                driver.quit()

            # xử lý link báo tuổi trẻ
            if url_to_scrape in ['https://tuoitre.vn/kinh-doanh/dau-tu.htm','https://tuoitre.vn/kinh-doanh/tai-chinh.htm','https://tuoitre.vn/kinh-doanh/doanh-nghiep.htm']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'list__listing-main'])
                headline = new_list.find('h3', ['class', 'box-title-text'])
                link = 'https://tuoitre.vn' + headline.find('a')['href']
                driver.quit()

            # Xử Lý báo VnExpress
            if url_to_scrape in ['https://vnexpress.net/kinh-doanh/vi-mo','https://vnexpress.net/kinh-doanh/quoc-te','https://vnexpress.net/kinh-doanh/doanh-nghiep','https://vnexpress.net/kinh-doanh/chung-khoan','https://vnexpress.net/kinh-doanh/bat-dong-san']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'col-left col-left-new col-left-subfolder'])
                headline = new_list.find('h2', ['class', 'title-news'])
                link = headline.find('a')['href']
                driver.quit()


            # Xử Lý báo VTV
            if url_to_scrape in ['https://vtv.vn/kinh-te.htm']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'list_news timeline'])
                headline = new_list.find('h4')
                link = 'https://vtv.vn' + headline.find('a')['href']
                driver.quit()


            # Xử Lý báo Chính Phủ
            if url_to_scrape in ['https://chinhphu.vn/tin-noi-bat-68258']:
                driver = get_headless_chrome_driver()
                driver.get(url_to_scrape)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_list = soup.find('div', ['class', 'col-lg-10'])
                headline = new_list.find('h2', ['class', 'Title'])
                link = headline.find('a')['href']
                driver.quit()

    
            if link:
                chat_id = TELEGRAM_CHANNEL_NAME
                try:
                    # Check if the message has been sent before
                    if link not in sent_link:
                        summary = summarize_news(link) # Use the new function
                        message = ''
                        message += f'<b>{headline.a.string.strip()}</b>\n - <b>A.I tóm tắt</b>:{summary}\n - Xem chi tiết: {link}\n'
                        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                        sent_link.append(link)
                        print(f"Message sent to {chat_id}")
                    else:
                        print("Message has already been sent")
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
                delete_oldest_link()
                break
        except Exception as e:
            print(f"Connection error: {e}")
    if _ == 4:
        print("Connection failed")



async def main():
    while True:
        for x in url_newspaper:
            await getnew(x)
  
        time.sleep(SCRAPING_INTERVAL_SECONDS)

asyncio.run(main())

# turn pyhton file to exe
# pyinstaller --onefile --icon=icon.ico phongvien.py