import asyncio
import json
from random import random
from names import Name
import discord
import requests
from discord.ext import commands
import movies

import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="l.", intents=intents)
config = {}
names = Name("", [])
async def movie_init():
    dune = movies.movies("Dune")
    dune.add_response(*("Omg I LOVE Dune, Paul Atreides is sooo attractive", "Dune is the best book ever written",
                 "I wish I could live in the Dune universe",
                 "Every once in a while, I remember that Dune exists and I get really happy, then I remember that I'm not in the Dune universe and I get really sad",
                 "I'm not a fan of Dune, but I respect your opinion", "Dune is a great book, but it's not for me",
                 "I've never read Dune, but I've heard it's good", "Dune is overrated",
                 "Dune? Reminds me of the deserts from my deployment in Iraq", "Dune is a classic",
                 "Paul Atreides makes me feel things ;))", "Heyyyyyy, wanna talk about Dune?"))



def get_words_by_pos(pos, max_results=50):
    words = set()
    for synset in wordnet.all_synsets(pos):
        for lemma in synset.lemmas():
            words.add(lemma.name())
        if len(words) >= max_results:
            break
    return list(words)[:max_results]


nouns = get_words_by_pos(wordnet.NOUN, 50)
adjectives = get_words_by_pos(wordnet.ADJ, 50)
verbs = get_words_by_pos(wordnet.VERB, 50)


async def main():
    #names.new_names()
    await movie_init()
    global config
    config = await importConfig()
    names.set_key(config['ninjaAPI'])

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
    await client.change_presence(activity=discord.Game(name="with a side of Pepsi"))
    #sync commands
    await client.get_cog("Commands").sync_commands()


@client.event
async def on_message(message):
    # Don't let the bot respond to its own messages
    if message.author == client.user:
        return

    content = message.content
    content = content.replace("l.noun", nouns[int(random() * len(nouns))])
    content = content.replace("l.adjective", adjectives[int(random() * len(adjectives))])
    content = content.replace("l.verb", verbs[int(random() * len(verbs))])
    if content.find("l.name") != -1:
        content = content.replace("l.name", names.get_name())

    if content != message.content:
        await message.channel.send("Surely you meant:\n" + content)

    if "dune" in message.content.lower():
        await message.add_reaction("🐛")
        await message.channel.send(movies.movie_list["Dune"].get_response())
    if "nuts" in message.content.lower():
        await message.add_reaction("🥜")
    if "deez" in message.content.lower():
        await message.add_reaction("🥜")
    if "mommy" in message.content.lower():
        await message.add_reaction("🤨")
    if "salami" in message.content.lower():
        await message.add_reaction("😳")
    if "joe" in message.content.lower():
        await message.add_reaction("😏")
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

def get_words_by_pos(pos, max_results=50):
    words = set()
    for synset in wordnet.all_synsets(pos):
        for lemma in synset.lemmas():
            words.add(lemma.name().replace("_", " "))
        if len(words) >= max_results:
            break
    return list(words)[:max_results]



if __name__ == '__main__':
    asyncio.run(main())
