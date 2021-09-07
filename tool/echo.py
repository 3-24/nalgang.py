#!/usr/bin/python3
import discord
import os

TOKEN = os.environ["echo_TOKEN"]
client = discord.Client()


@client.event
async def on_ready():
    print('Echo bot is ready')


@client.event
async def on_message(message):
    if message.author.bot:
        return

    await message.channel.send(message.content)

client.run(TOKEN)
