import asyncio
import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="l.", intents=intents)
config = {}

async def main():
    global config

    config = await importConfig()

    if not config:
        config = {}
        config['token'] = input("Enter your bot token: ")
        config['prefix'] = "l."
        with open('config.json', 'w') as f:
            json.dump(config, f)

    # Load the commands
    client.remove_command("help")
    print("Loading the commands extension")  # Debug print statement
    await client.load_extension('commands')

    # Run the bot
    await client.start(config['token'])




@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


async def importConfig():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("Config file not found, creating a new one")
        print("Please fill in the token with your bot token and restart the bot.")
        return None


if __name__ == '__main__':
    asyncio.run(main())
