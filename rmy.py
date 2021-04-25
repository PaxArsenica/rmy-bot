import os

import discord
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import Embed, Color
from aiohttp import ClientSession
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import schedule
import time

client = discord.Client()

# Loads env file with Discord Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot_prefix = '!rmy'

opts = ChromeOptions()
opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-sh-usage")

driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=opts)

#Sub of the Week
sotw = ''

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith(bot_prefix):
        return

    args = message.content[len(bot_prefix):].strip().split(' ')

    print(args)

    if args [0] == 'about':
        return
    
    if args [0] == 'help':
        return

    # Command Level
    if args[0] == 'pubsub':
        print('sub of da week: ' + sotw)
        await message.channel.send(f'This week\'s Publix Sub is the {get_sub()}!')


def get_sub_of_the_week():
    print('Fetching Sub of the Week...')
    try:
        set_publix_store()
        driver.get('https://www.publix.com/savings/weekly-ad')
        driver.find_element_by_xpath("//a[@id='deli']").click()
        sub = driver.find_element_by_xpath("//div[contains(text(),'Whole Sub')]").text
        global sotw
        sotw = sub
        print('Sub successfully retrieved!')
        return sub
    except:
        print('There was an error while retrieving the sub of the week.')

def get_sub():
    if sotw != '':
        print('Sub already retrieved')
        return sotw
    else:
        return get_sub_of_the_week()

def set_publix_store():
    driver.get('https://www.publix.com/savings/weekly-ad')
    driver.implicitly_wait(4)
    try:
        driver.find_element_by_xpath("//button[contains(text(),'Choose a Store')]").click()
        driver.find_element_by_xpath("//input[@id='input_ZIPorCity,Stateorstorenumber102']").send_keys("30301")
        driver.find_element_by_xpath("//button[@name='Store Search Button']").click()
        driver.implicitly_wait(4)
        driver.find_element_by_xpath("//button[contains(text(),'Choose Store')]").click()
    except:
        print('Store already selected')

def run_continuously():
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(1)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

schedule.every().wednesday.at('11:00').do(get_sub_of_the_week)

# Start the background thread
run_continuously()

client.run(TOKEN)