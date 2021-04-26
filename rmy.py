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
from apscheduler.schedulers.background import BackgroundScheduler
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

scheduler = BackgroundScheduler()

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
        sub_response = get_sub_of_the_week() if (len(args) == 2 and args[1] == 'update') else get_sub()
        if sub_response != '':           
            await message.channel.send(f'This week\'s Publix Sub is the {sub_response}!')
        else:
            await message.channel.send('There was an error while retrieving the Sub of the Week. Please try again later.')

    if args[0] == 'flaccid':
        await message.channel.send('https://tenor.com/view/meryl-streep-flacid-gif-10066576')

def get_sub_of_the_week():
    global sotw
    i = 0
    while i < 3:
        print('Fetching Sub of the Week...')
        try:
            set_publix_store()
            driver.get('https://www.publix.com/savings/weekly-ad')
            driver.find_element_by_xpath("//a[@id='deli']").click()
            sotw = driver.find_element_by_xpath("//div[contains(text(),'Whole Sub')]").text
            print('Sub successfully retrieved.')
            break
        except:
            print('There was an error while retrieving the sub of the week.')
        i += 1
    return sotw

def get_sub():
    if sotw != '':
        print('Sub already retrieved.')
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
        print('Store already selected.')


@scheduler.scheduled_job('cron', day_of_week='wed', hour=11)
def get_sub_of_the_week_scheduler():
    print('getting subs')
    get_sub_of_the_week()

scheduler.start()
client.run(TOKEN)