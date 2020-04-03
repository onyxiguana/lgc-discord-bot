import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import random
import re
import requests

bot = commands.Bot(command_prefix='!')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases=["aisays","frankiesays","leandrosays"])
async def badproverb(ctx):
    with open('messages.txt', 'r') as messagefile:
        proverbs = [proverb.rstrip('\n') for proverb in messagefile]
        await ctx.send(random.choice(proverbs))

@bot.command(aliases=["aisaid","frankiesaid","leandrosaid"])
async def newbadproverb(ctx, *newproverb):
    newproverb = ' '.join(newproverb)
    if newproverb is '':
        message = """Either type your new proverb after the command, e.g. "!aisaid Whoever has four corners should resign",
        or use !badproverb to hear one of our proverbs."""
        embed = discord.Embed(title="Remember to type your proverb!",
                              description=message, color=0xeee657)
        embed.set_thumbnail(url=random.choice([
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/USAF_B-2_Spirit.jpg/200px-USAF_B-2_Spirit.jpg",
        "http://art6.photozou.jp/pub/630/47630/photo/16803620_624.v1585627234.jpg",
        ]))
        await ctx.send(embed=embed)
    else:
        re.sub(r'[^a-zA-Z0-9,. ]','',newproverb)
        with open('messages.txt', 'a') as messagefile:
            messagefile.write(newproverb+'\n')
        await ctx.send('Added the new proverb "'+newproverb+'". Thanks!')


@bot.command()
async def welcomelinks(ctx):
    message = "Lancaster Go Club [[Facebook](https://www.facebook.com/groups/lancastergoclub)] [[play on OGS](https://online-go.com/group/2607)]\nBritish Go Association [[Homepage](http://britgo.org/)]\nEuropean Go Federation [[Homepage](https://eurogofed.org/)] [[EGD rankings database](http://www.europeangodatabase.eu/EGD/)]\nInternational Go Federation [[Homepage](https://www.intergofed.org/)]"
    embed = discord.Embed(title="Our club and surroundings",
                          description=message, color=7506394)
    await ctx.send(embed=embed)
    
@bot.command()
async def beginnerlinks(ctx):
    message = "**Learn the rules!** \n[The Interactive Way to Go ](http://playgo.to/iwtg/en/) (requires flash)\nA classic, often recommended, tutorial for learning the rules and much more. Alternatives that don't require Flash include [the OGS tutorial](https://online-go.com/learn-to-play-go), [learn-go.net](https://www.learn-go.net/) and [learn-go.now.sh](https://learn-go.now.sh/), but these cover less.\n\n**Once you know the rules...**\n[Online Go Server](https://online-go.com/) – Play, play, play! :smiley:\n[Gochild](http://gochild2009.appspot.com/) (refresh page to get it to work) – A big collection of Go problems starting from the basics. No instructions, but if you've seen the \"make two eyes\" concept, the problems will start to make sense.\n[Sensei's library](https://senseis.xmp.net/)  – The Go bible online. The [beginner pages](https://senseis.xmp.net/?PagesForBeginners) are a great place to start.\n\n**Or just watch...**\n[Hikaru no Go](https://en.wikipedia.org/wiki/Hikaru_no_Go) [[YouTube English dub](https://www.youtube.com/watch?v=ey657PxfXlM&list=PLaXkLkOnTTwGcmSowFho0Kb6Gw3UdP6Ta)] [[YouTube English sub](https://www.youtube.com/watch?v=k6e03IDZ9a0&list=PLjKsVS5ikMdDhVap-UAR_9kZMAB-TJREd)]\nAnother classic, a manga series responsible for a boom of young Go players in Japan and around the world. Aside from being a sweet coming-of-age story, this series will teach you the basics and culture of Go, and many of the games in it are real, professional games."
    embed = discord.Embed(title="Five websites for beginners",
                          description=message, color=7506394)
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
