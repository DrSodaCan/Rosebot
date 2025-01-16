from random import randint
from random import choice

import aiohttp
import discord
import requests
from discord.ext import commands
from PIL import Image

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        embedVar = discord.Embed(title="Help", description="List of commands", color=0x3F19F7)
        embedVar.add_field(name="crime", value="Check your crime coefficient. Input: @User", inline=False)
        embedVar.add_field(name="digimon", value="Get information about a digimon. Input: Name", inline=False)
        embedVar.add_field(name="mc_skin", value="Borrow someone's Minecraft skin. Input: username", inline=False)
        embedVar.add_field(name="quantize", value="Quantize an image. Required input: Image. Optional input: # of colors (default 256)", inline=False)
        embedVar.add_field(name="balance", value="Check your Lunacoin balance", inline=False)
        embedVar.add_field(name="pay", value="Send Lunacoins to someone. Input: @User, amount", inline=False)
        return await ctx.send(embed=embedVar)


    @commands.command(name='crime')
    async def crime(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("You need to mention a user!")
            return

        crime_coefficient = randint(0, 350)
        embedVar = discord.Embed(title="", color=0x3F19F7)

        match crime_coefficient:
            case 0:
                embedVar.title = f"{member.display_name}'s crime coefficient is OVER 9000?? There's no way that could be right"
                embedVar.set_image(url="https://c.tenor.com/x_GNnWa8SIoAAAAC/tenor.gif")
            case x if 1 <= x <= 99:
                embedVar.title = f"{member.display_name}'s crime coefficient is {crime_coefficient}. They're a jolly fellow"
                embedVar.set_image(url="https://media1.tenor.com/m/cu5y-tYcCPYAAAAd/psycho-pass-nobuchika-ginoza.gif")
            case x if 100 <= x <= 199:
                embedVar.title = f"{member.display_name}'s crime coefficient is {crime_coefficient}. Things ain't so shrimple here..."
                embedVar.set_image(url="https://media1.tenor.com/m/mBRKaardPOUAAAAC/anime-pyschopass.gif/")
                embedVar.color = 0x7019F7
            case x if 200 <= x <= 299:
                embedVar.title = f"{member.display_name}'s crime coefficient is {crime_coefficient}. They're a latent criminal."
                embedVar.set_image(url="https://media1.tenor.com/m/Ss_HqElFq4EAAAAC/psycho-pass-akane-tsunemori.gif")
                embedVar.color = 0xD819F7
            case _:
                embedVar.title = f"{member.display_name}'s crime coefficient is {crime_coefficient}. They're a MENACE."
                embedVar.set_image(url="https://media1.tenor.com/m/LhMnSAIglNsAAAAd/psycho-pass-dominator.gif")
                embedVar.color = 0xF71954
        return await ctx.send(embed=embedVar)

    @commands.command(name='digimon')
    async def digimon(self, ctx, name: str):
        url = f"https://digi-api.com/api/v1/digimon/{name}"
        response = requests.get(url)
        data = response.json()
        if not data:
            return await ctx.send("No digimon found with that name!")
        name = data['name']

        image = data['images'][0]['href']
        embedVar = discord.Embed(title=name, color=0x3F19F7)

        embedVar.add_field(name="Level", value=data['levels'][0]['level'])
        embedVar.add_field(name="Description", value=data['descriptions'][1]['description'])

        embedVar = embedVar.set_image(url=image)

        #Debug: print it to console

        return await ctx.send(embed=embedVar)
    @commands.command(name='mc_skin')
    async def mc_skin(self, ctx, username: str):
        url = f"https://playerdb.co/api/player/minecraft/{username}"
        response = requests.get(url)
        if response.status_code == 204:
            return await ctx.send("No player found with that username!")
        if response.response_code == 429:
            return await ctx.send("Rate limit exceeded, try again later.")
        elif response.status_code != 200:
            return await ctx.send("An error occurred while fetching the skin.")
        skin = response.json()['data']['player']['skin_texture']
        embedVar = discord.Embed(title=f"{username}'s Minecraft Skin", color=0x3F19F7)
        embedVar.set_image(url=skin)
        return await ctx.send(embed=embedVar)
    @commands.command(name='quantize')
    async def quantize(self, ctx, colors=256):
        if len(ctx.message.attachments) == 0:
            return await ctx.send("You need to attach an image!")
        attachment = ctx.message.attachments[0]
        image = Image.open(requests.get(attachment.url, stream=True).raw)
        image = image.quantize(colors=colors)
        image.save("output.png")
        await ctx.send(file=discord.File("output.png"))

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, question):
        options = ["Yes", "No", "Ask Later", "Maybe", "Probably", "Probably Not"]
        output = choice(options)
        output = "> 🎱 " + output
        await ctx.send(output)


    #Lunacoin commands: balance, send, request, link to mc account leaderboard
    @commands.command(name='create_lunacoin_account')
    async def create_lunacoin_account(self, ctx):
        #API: https://localhost:7072/Create
        #Input: requires JSON with:
        # discordID: ctx.author.id
        # balance: 100
        #SSL is disabled for now

        url = f"https://localhost:7072/User"
        user_data = {
            "username": ctx.author.name,
            "discordId": str(ctx.author.id),
            "balance": 100.00
        }
        print(user_data)
        requests.post(url, json=user_data, verify=False)

        return await ctx.send("Account created successfully! You have a balance of: 100.00 Lunacoins")

    @commands.command(name='balance')
    async def balance(self, ctx):
        url = f"https://localhost:7072/discordID/{ctx.author.id}"
        print(url)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, ssl=False) as response:
                    print("Response: ", response.status)
                    if response.status == 404:
                        await ctx.send("You don't have a Lunacoin account yet! Creating one now...")
                        print("Creating account")
                        return await self.create_lunacoin_account(ctx)
                    if response.status != 200:
                        print(response.status)
                        return await ctx.send("An error occurred while fetching your balance.")

                    data = await response.json()
                    print(data)
                    balance = data['balance']
                    return await ctx.send(f"Your balance is: {balance}")
            except aiohttp.ClientError as e:
                print(f"Request failed: {e}")
                await ctx.send("An error occurred while fetching your balance.(Server is down)")





    @commands.command(name='pay')
    async def pay(self, ctx, recipient: discord.Member, amount: float):
        url = f"https://localhost:7072/Transfer"
        user_data = {
            "SenderDiscordId": ctx.author.id,
            "RecipientDiscordId": recipient.id,
            "Amount": amount
        }
        requests.post(url, json=user_data, verify=False)

        if not requests.status_code == 200:
            return await ctx.send("An error occurred while sending the payment.")
        return await ctx.send(f"Payment of {amount} Lunacoins sent to {recipient.display_name}. (Server is down)")




    @commands.command(name='pay_debug')
    async def pay_debug(self, ctx):
        url = f"https://localhost:7072/Transfer"
        user_data = {
            "senderDiscordId": 153340370661539841,
            "recipientDiscordId": 1201739913205121034,
            "amount": 25
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=user_data, ssl=False) as response:
                    print("Response: ", response.status)
                    if response.status != 200:
                        return await ctx.send("An error occurred while sending the payment.")
                    return await ctx.send(f"Payment of {user_data['Amount']} Lunacoins sent to recipient")
            except aiohttp.ClientError as e:
                print(f"Request failed: {e}")
                await ctx.send("An error occurred while sending the payment.")







async def setup(bot):
    print("Setting up the cog")  # Debug print statement
    await bot.add_cog(Commands(bot))
