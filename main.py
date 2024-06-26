import asyncio
import json
from random import random

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="l.", intents=intents)
config = {}
dune_messages = ["Omg I LOVE Dune, Paul Atreides is sooo attractive", "Dune is the best book ever written",
                 "I wish I could live in the Dune universe",
                 "Every once in a while, I remember that Dune exists and I get really happy, then I remember that I'm not in the Dune universe and I get really sad",
                 "I'm not a fan of Dune, but I respect your opinion", "Dune is a great book, but it's not for me"]
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
    await client.change_presence(activity=discord.Game(name="Dune"))
@client.event
async def on_message(message):
    # Don't let the bot respond to its own messages
    if message.author == client.user:
        return
    #If the message contains the word "Dune", respond with a random message from the list
    if "dune" in message.content.lower():
        await message.add_reaction("🐛")
        await message.channel.send(dune_messages[int(random() * len(dune_messages))])
    await client.process_commands(message)


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
