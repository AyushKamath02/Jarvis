import discord
from discord.ext import commands
import os
import requests
import json
import io
import aiohttp
import googlesearch
import random
import asyncio
import youtube_dl
from discord.utils import get
from youtube_search import YoutubeSearch

TOKEN = "Bot token goes here"
bot = commands.Bot(command_prefix="!")

games = {
    'Flip a Coin': "!coinflip",
    'Roll a dice with n sides. Defaults to 6': "!diceroll <num of sides>",
    'Guess the Number': "!guessnum",
    'Check out a random trivia question': '!trivia',
}

command_list = {
    'Greeting': "!hello",
    'Thank you': "!thankyou",
    'Judge a bad song': '!badsong',
    'Random quote': "!myjuice",
    'Get an activity to do': "!imbored",
    'Get a joke': "!needlaugh",
    'Get an inspirational message': "!inspire",
    'Get Top 3 search results from Google': "!search <query>",
    'Check 5 trending news articles': '!news',
    'Check out the current weather stats': '!weather <zipcode>',
    'Get a random picture of a fox': "!pic",
    'List the minigames available': "!minigames",
    "Try to guess the number I'm thinking of": "!guess num <your guess>",
    "**Here are the audio commands**": "",
    "\t\tJoin voice channel": "!join",
    "\t\tPlay a YouTube video": "!play <url>",
    "\t\tLeave voice channel": "!leave",
    "\t\tPause currently playing audio": "!pause",
    "\t\tResume paused audio": "!resume",
    "\t\tStop the audio": "!stop",
    "View the list of commands": "!help"
}


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + "\n")


# @bot.command(pass_context= True) #
@bot.command(pass_context=True, aliases = ['Hello', 'hell o'])
async def hello(ctx):
    await ctx.send("Hello!")


@bot.command(pass_context=True , aliases = ["Thankyou", "Thank you", "thank you", "Thank You", "ThankYou"])
async def thankyou(ctx):
    await ctx.send("You're Welcome!")

@bot.command(pass_context=True)
async def badsong(ctx):
    await ctx.send("I agree with you on this one. 0/10.")


@bot.command(pass_context=True)
async def myjuice(ctx):
    response = requests.get("https://zenquotes.io/api/random")
    jason = json.loads(response.text)
    quote = jason[0]['q'] + " -by " + jason[0]['a']
    await ctx.send(quote)


@bot.command(pass_context=True)
async def imbored(ctx):
    res = requests.get("https://www.boredapi.com/api/activity")
    jason = json.loads(res.text)
    await ctx.send(jason["activity"])


@bot.command(pass_context=True)
async def needlaugh(ctx):
    response = requests.get(
        "https://official-joke-api.appspot.com/random_joke")
    jason = json.loads(response.text)
    await ctx.send(jason["setup"])
    await ctx.send(jason['punchline'])


@bot.command(pass_context=True)
async def trivia(ctx):
    options = []
    string = ""
    response = requests.get(
        "https://opentdb.com/api.php?amount=1&type=multiple")
    jason = json.loads(response.text)
    right_ans = jason['results'][0]['correct_answer']
    options.append(right_ans)
    for inco in jason['results'][0]['incorrect_answers']:
        options.append(inco)
    print(options)
    difficulty = jason["results"][0]["difficulty"]
    category = jason["results"][0]['category']
    await ctx.send(
        f"**This is a {difficulty} difficulty question in the {category} category**"
    )
    await ctx.send(str(jason["results"][0]["question"]))
    random.shuffle(options)
    print(options)
    for option in options:
        string += f"> {option} \n"
    await ctx.send(string)
    await ctx.send("I'll wait for 15 seconds so you can think about it")
    await asyncio.sleep(15)
    await ctx.send(f"Correct answer: {right_ans}")


@bot.command(pass_context=True)
async def inspire(ctx):
    response = requests.get("https://www.affirmations.dev/")
    jason = json.loads(response.text)
    await ctx.send(jason['affirmation'])


@bot.command(pass_context=True)
async def pic(ctx):
    response = requests.get("https://randomfox.ca/floof")
    jason = json.loads(response.text)
    link = jason["image"]
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file...')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'cool_image.png'))


@bot.command(pass_context=True)
async def search(ctx, *queries):
    final_query = " ".join(queries)
    await ctx.send(f"Now searching for: {final_query} on Google")
    for res in googlesearch.search(
            final_query, tld="com", num=3, start=0, stop=3, pause=2):
        await ctx.send(res)


@bot.command(pass_context=True)
async def news(ctx):
    string = ""
    response = requests.get(
        "https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey=12f953e7e4db46629eeb6f1c4297eca3"
    )
    if response.status_code == 429:
        await ctx.send(
            "You have used up all your requests for the day. Please try later")
    else:
        jason = json.loads(response.text)
        length = len(jason['articles'])
        print(f"Length is {length}")
        await ctx.send("Here is your news briefing!")
        for i in range(5):
            rand_num = random.randint(0, length - 1)
            print(rand_num)
            await ctx.send(jason['articles'][rand_num]['url'])
            await asyncio.sleep(0.5)
            del jason['articles'][rand_num]
            length -= 1


@bot.command(pass_context=True)
async def weather(ctx, *args):
    parm = " ".join(args)
    if len(args) == 1:
        string = ""
        try:
            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?zip={args[0]}&appid=8e543b10eaf9e628b685a69152682b1d"
            )
            jason = json.loads(response.text)
            await ctx.send(
                f"**Here is the current weather report for {jason['name']}:**")
            current_temp = int((float(jason['main']['temp']) - 273.15) * 1.8 +
                                32)
            string += f"Current temp: {current_temp}\n"
            fl_temp = int((float(jason['main']['feels_like']) - 273.15) * 1.8 +
                            32)
            string += f"Feels like: {fl_temp}\n"
            high_temp = int((float(jason['main']['temp_max']) - 273.15) * 1.8 +
                            32)
            string += f"Today's High: {high_temp}\n"
            low_temp = int((float(jason['main']['temp_min']) - 273.15) * 1.8 +
                            32)
            string += f"Today's Low: {low_temp}\n"
            await ctx.send(string)
            await ctx.send(
                f"The weather right now is: {jason['weather'][0]['description']}")
        except KeyError:
            if args[0].lower() == "yomama":
                await ctx.send("Yo mama so fat, when she farts she creates toxic clouds in the atmosphere")
            else:
                await ctx.send("Please give a valid zipcode. ")
    elif parm.lower() == "yo mama":
        await ctx.send("Yo mama so fat, when she farts she creates toxic clouds in the atmosphere")
    else:
        await ctx.send("Please give a valid zipcode.")


@bot.command(pass_context=True)
async def minigames(ctx):
    string = ""
    for key, value in games.items():
        string += f"{key}: {value}\n" 
    await ctx.send(string)


@bot.command(pass_context=True)
async def coinflip(ctx):
    choice = random.choice(['Heads', 'Tails'])
    await ctx.send(f"I got: {choice}")


@bot.command(pass_context=True)
async def diceroll(ctx, max):
    try:
        end = int(max)
        num = random.randint(1, end)
        await ctx.send(f"I got a: {num}")
    except:
        await ctx.send("Please input an integer")



@bot.command(pass_context=True)
async def guessnum(ctx, arg=None):
    comp_num = random.randint(1, 10)
    if arg == None:
            await ctx.send("Please for the love of christ enter a number between 1 and 10")
    else:
        try:
            guess = int(arg)
            if guess:
                if guess > 10 or 0 > guess:
                    await ctx.send("Please enter a number between 1 and 10")
                else:
                    await ctx.send(f"Your guess: {guess}")
                    await ctx.send(f"My answer: {comp_num}")
                    if guess == comp_num:
                        await ctx.send("You're a god!")
                    else:
                        dif = abs(comp_num - guess)
                        await ctx.send(f"You were {dif} off")
                        await ctx.send("Better luck next time")
            
        except:
            await ctx.send("Please enter a number between 1 and 10")  

@bot.command(pass_context=True)
async def commands(ctx):
    string = ""
    for key, value in command_list.items():
        string += f"{key} : {value}\n"
    await ctx.send(string)


@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)

    await channel.connect()

    await ctx.send(f"Joined {channel}")


@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"Left {channel}")
    else:
        await ctx.send("I am not in a voice channel")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):
    def searchyt(terms):
        query = " ".join(terms)
        results = YoutubeSearch(query, max_results=1).to_dict()
        return results
    
    if len(url) > 1:
        res = searchyt(url)
        query = f"https://youtube.com/watch?v={res[0]['id']}"
    elif len(url) == 1:
        query = url[0]


    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([query])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")


@bot.command(pass_context=True)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("Music Paused")
    else:
        await ctx.send("No music is playing.")


@bot.command(pass_context=True)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("Music Resumed")
    else:
        await ctx.send("Music is not paused")


@bot.command(pass_context=True)
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Music Stopped")
    else:
        await ctx.send("No Music is playing")


bot.run(TOKEN)

