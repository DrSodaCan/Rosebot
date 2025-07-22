import asyncio
import json
from random import random
from names import Name
import discord
from discord.ext import commands
import replier

import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="l.", intents=intents)
config = {}

reactions = {"joe": "😏",
             "deez": "🥜",
             "nut": "🥜",
             "mommy": "🤨"}
names = Name("", [])
async def movie_init():
    dune = replier.movies("Dune")
    dune.add_response(*("Omg I LOVE Dune, Paul Atreides is sooo attractive", "Dune is the best book ever written",
                 "I wish I could live in the Dune universe",
                 "Every once in a while, I remember that Dune exists and I get really happy, then I remember that I'm not in the Dune universe and I get really sad",
                 "I'm not a fan of Dune, but I respect your opinion", "Dune is a great book, but it's not for me",
                 "I've never read Dune, but I've heard it's good", "Dune is overrated",
                 "Dune? Reminds me of the deserts from my deployment in Iraq", "Dune is a classic",
                 "Paul Atreides makes me feel things", "Heyyyyyy, wanna talk about Dune?"))
    naruto = replier.movies("Naruto")
    naruto.add_response(*("Pshh, weebs amirite?", "Naruto is overrated",
                          "Believe it! …or don't.", "Sasuke was better anyway.",
                          "Naruto fans are built different."))


    pomni = replier.movies("Pomni")
    pomni.add_response(*("she just like me frfr",
                         "https://tenor.com/view/the-pomni-song-the-amazing-digital-circus-pomni-digital-circus-pomni-my-name-is-pomni-and-i-can%E2%80%99t-escape-the-digital-circus-gif-930457201671946760",
                         "I wake up everyday thinking I'm stuck in a digital circus too."))
    crazy = replier.movies("Crazy")
    crazy.add_response(*("Crazy? I was crazy once. They put me in a room. A rubber room. A rubber room with rats. and rats make me crazy",
                         "https://tenor.com/view/cat-wiggle-crazy-cat-zoomies-gif-9877358298643393466"),
                       )
    bocchi = replier.movies("Bocchi")
    bocchi.add_response(*("She just like me frfr", "Bocchi just GETS me yknow.",
                          "Bocchi for president.", "What if… Bocchi was real?"))
    tea = replier.movies("Tea")
    tea.add_response(*("omg yass girl what's the tea?", "omg gurl spill it queen!!"))
    sonic = replier.movies("Sonic")
    sonic.add_response(*("I miss my wife, tails :pensive: I miss her lots", "Shadow just GETS me yknow", "Rolling around at the speed of sound",
                         "Keanu Reeves as Shadow is the best cinematic decision ever."))
    namedrop = replier.movies("rosebot")
    namedrop.add_response(*("heyy bestie", "hiiiiiiii :3", "uwu", "nyaaa 🐈"))



def get_words_by_pos(pos, max_results=50):
    words = set()
    for synset in wordnet.all_synsets(pos):
        for lemma in synset.lemmas():
            words.add(lemma.name())
        if len(words) >= max_results:
            break
    return list(words)[:max_results]


def refill_if_needed(word_list, pos, threshold=10, refill_amount=50):
    if len(word_list) < threshold:
        new_words = get_words_by_pos(pos, refill_amount)
        word_list.extend([word.replace('_', ' ') for word in new_words])

nouns = get_words_by_pos(wordnet.NOUN, 50)
nouns = [noun.replace('_', ' ') for noun in nouns]
adjectives = get_words_by_pos(wordnet.ADJ, 50)
verbs = get_words_by_pos(wordnet.VERB, 50)


async def main():
    #names.new_names()
    await movie_init()
    global config
    config = await importConfig()

    if not config:
        config = {}
        config['token'] = input("Enter your bot token: ")
        config['prefix'] = "l."
        config['ninjaAPI'] = ""
        with open('config.json', 'w') as f:
            json.dump(config, f)
    try:
        names.set_key(config['ninjaAPI'])
    except KeyError:
        print("No Ninja API found. Cannot use Name generator")

    # Load the commands
    client.remove_command("help")
    print("Loading the commands extension")  # Debug print statement
    await client.load_extension('commands')

    # Run the bot
    await client.start(config['token'])



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="Tetris"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content

    if "l.noun" in content and nouns:
        word = nouns.pop(int(random() * len(nouns)))
        content = content.replace("l.noun", word, 1)
        refill_if_needed(nouns, wordnet.NOUN)

    if "l.adjective" in content and adjectives:
        word = adjectives.pop(int(random() * len(adjectives)))
        content = content.replace("l.adjective", word, 1)
        refill_if_needed(adjectives, wordnet.ADJ)

    if "l.verb" in content and verbs:
        word = verbs.pop(int(random() * len(verbs)))
        content = content.replace("l.verb", word, 1)
        refill_if_needed(verbs, wordnet.VERB)

    if "l.name" in content:
        content = content.replace("l.name", names.get_name())

    if content != message.content:
        await message.channel.send("Surely you meant:\n" + content)

    for movie_name, movie_obj in replier.movie_list.items():
        if movie_name.lower() in content.lower():
            await message.channel.send(movie_obj.get_response())
            break

    if "dune" in message.content.lower():
        await message.add_reaction("🐛")
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
