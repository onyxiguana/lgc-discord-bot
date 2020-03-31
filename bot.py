import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import random
import re
import requests

bot = commands.Bot(command_prefix='b!')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases=["aisays","frankiesays","leandrosays"])
async def badproverb(ctx):
    messages = [
        "A wise person always leaves an even number of weak groups.",
        "Memorising Joseki is all you need to become a strong Go player.",
        "One eye beats two eyes.",
        "One eye is all you need to live.",
        "Only a moron connects against a peep.",
        "Play where your opponent wants you to play.",
        "Proverbs are never wrong.",
        "When in a life-and-death situation, tenuki!",
        "When in doubt, play the empty triangle."
    ]
    await ctx.send(random.choice(messages))

@bot.command()
async def welcomelinks(ctx):
    message = "Lancaster Go Club [[Facebook](https://www.facebook.com/groups/lancastergoclub)] [[play on OGS](https://online-go.com/group/2607)]\nBritish Go Association [[Homepage](http://britgo.org/)]\nEuropean Go Federation [[Homepage](https://eurogofed.org/)] [[EGD rankings database](http://www.europeangodatabase.eu/EGD/)]\nInternational Go Federation [[Homepage](https://www.intergofed.org/)]"
    embed = discord.Embed(title="Our club and surroundings",
                          description=message, color=7506394)
    await ctx.send(embed=embed)
    
@bot.command()
async def beginnerlinks(ctx):
    message = "To search in Sensei's Library, please add a term as: !sensei term\n\nNOTE: Leave out spaces!"
    embed = discord.Embed(title="Please add a search term",
                          description=message, color=0xeee657)
    embed.set_thumbnail(url="https://senseis.xmp.net/images/stone-hello.png")
    await ctx.send(embed=embed)
    
@bot.command(pass_context=True, aliases=["define"])
async def sensei(ctx, term=None):
    """Get information from Sensei's Library."""
    if term is None:
        message = "To search in Sensei's Library, please add a term as: !sensei term\n\nNOTE: Leave out spaces!"
        embed = discord.Embed(title="Please add a search term",
                              description=message, color=0xeee657)
        embed.set_thumbnail(url="https://senseis.xmp.net/images/stone-hello.png")
        await ctx.send(embed=embed)
    else:
        s = requests.Session()
        url = "https://senseis.xmp.net/"
        s.headers.update({'referer': url})
        params = {'searchtype': 'title',
                  'search': term
                  }
        # Get all results searching by title
        r = s.get(url, params=params)

        # Separate direct hit
        regex = (r"\<b\>Direct hit\:\<br\>\<a href=\"\/\?(?P<term_url>.*?)\"" +
                 r"\>(?P<term>.*?)\<\/a\>\<\/b\>")
        match = re.search(regex, r.text, re.IGNORECASE)
        if match:
            url = "https://senseis.xmp.net/?" + match.group('term_url')
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            title = "**" + soup.title.string + "**"
            message = paragraphs[1].text + "\n"
            message += "[See more online]({}) on Sensei's Library.".format(url)
        else:
            title = "**The term '{}' was not found**".format(term)
            message = ("The exact term {} was not found on".format(term) +
                       " Sensei's Library.")
        embed = discord.Embed(title=title, description=message, color=0xeee657)
        embed.set_thumbnail(url="https://senseis.xmp.net/images/stone-hello.png")

        # Search for non-direct hits containing the words
        regex = (r"\<b\>Title containing word( starting with search term)?" +
                 r"\:\<\/b\>\<br\>\n(?:<img .*?)?(?:<a href=\"" +
                 r"/\?(.*?)\">(.*?)</a>.*?\n){1,5}")
        match = re.search(regex, r.text, re.MULTILINE)

        # If there are alternatives, add them in the embed
        if match:
            groups = match.group(0).split("\n")[1:-1]
            value = ""
            for index in range(0, len(groups)):
                regex = r'<a href=\"/\?(?P<term_url>.*?)\"\>(?P<term>.*?)</a>'
                match = re.search(regex, groups[index])
                if match:
                    value += ("[{}](https://senseis.xmp.net/?" +
                              "{})\n").format(match.group("term"),
                                              match.group("term_url"))

            embed.add_field(name='Alternative search terms:',
                            value=value,
                            inline=False)
        else:
            embed.add_field(name="Alternative search terms",
                            value="No alternative terms found.", inline=False)
        await ctx.send(embed=embed)

bot.run(os.environ['TOKEN'])
