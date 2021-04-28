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

client = discord.Client()

# Loads env file with Discord Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PERSONAL_FINANCE = os.getenv('PERSONAL_FINANCE_CHANNEL_ID')
bot_prefix = '!rmy'

commands_dict = {
    'about': 'A brief description of the purpose and functionality of this Discord bot.',
    'commands': 'I wonder what this does... :thinking:',
    'pubsub': 'What\'s on the menu this week? This command retrieves Publix\'s sub sandwich that is on sale this week.',
    'flaccid': 'Wanna let the world know you love flaccid fries? Use this command!',
    'Others:': 'loot, roth, bot'
}

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
        rmy_bot_logo = discord.File("./img/rmybot.png", filename="rmybot.png")
        about_embed = discord.Embed(title='RMY Bot', color=discord.Color.red(), description='My name is RMY Bot v0.1. My purpose is to entertain the members of RMY with fun and useful commands. Type `!rmy commands` to learn more about what I can do.')
        about_embed.set_image(url='attachment://rmybot.png')
        await message.channel.send(file=rmy_bot_logo, embed=about_embed)
    elif args [0] == 'commands':
        command_embed = discord.Embed(title='RMY Bot Commands', color=discord.Color.red(), description='Here\'s a list of my commands:')
        for command in commands_dict:
            command_embed.add_field(name=command, value=commands_dict[command], inline=False)
        await message.channel.send(embed=command_embed)
    # Commands
    elif args[0] == 'pubsub':
        sub_response = get_sub_of_the_week() if (len(args) == 2 and args[1] == 'update') else get_sub()
        if sub_response != '':           
            await message.channel.send(f'This week\'s Publix Sub is the {sub_response}!')
            if sub_response.find('Tender') != -1:
                await message.channel.send('https://tenor.com/view/lets-go-lets-goo-lest-gooooooooooooooooo-gif-19416648')
        else:
            await message.channel.send('There was an error while retrieving the Sub of the Week. Please try again later.')
    elif args[0] == 'roth':
        await message.channel.send(f'You telling me you don\'t have a Roth IRA? You better open one up right mf now! And while you\'re at it, check out my guide to personal finance (see the pinned post in the <#{PERSONAL_FINANCE}> channel)!')
    elif args[0] == 'loot':
        await message.channel.send('It wouldn\'t be me if I didn\'t loot.')
    elif args[0] == 'bot':
        await message.channel.send('https://thumbs.gfycat.com/BonyLonelyDesertpupfish-size_restricted.gif')
    elif args[0] == 'flaccid':
        await message.channel.send('https://tenor.com/view/meryl-streep-flacid-gif-10066576')
    else:
        await message.channel.send('I don\'t recognize that command. Please type `!rmy commands` to see a list of what I can do!')


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
    get_sub_of_the_week()

scheduler.start()
client.run(TOKEN)