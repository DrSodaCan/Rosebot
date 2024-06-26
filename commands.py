from random import randint
import discord
import requests
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        print(name)

        image = data['images'][0]['href']
        embedVar = discord.Embed(title=name, color=0x3F19F7)

        #embedVar.add_field(name="Level", value=data['level'])
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
async def setup(bot):
    print("Setting up the cog")  # Debug print statement
    await bot.add_cog(Commands(bot))
