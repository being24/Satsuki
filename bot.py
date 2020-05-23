# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import json
import os
import sys
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv


class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=None)

        self.INITIAL_COGS = [
            filename[:-3] for filename in os.listdir(currentpath + "/cogs")
            if filename.endswith(".py")]

        for cog in self.INITIAL_COGS:
            try:
                self.load_extension(f'cogs.{cog}')
            except Exception:
                traceback.print_exc()

        with open(currentpath + "/setting.json", encoding='utf-8') as f:
            self.json_data = json.load(f)

        self.send_max = self.json_data['limit']
        self.admin_id = self.json_data['admin']["id"]
        self.status = self.json_data['status']
        self.meeting_addr = self.json_data['regular_meeting_addr']

    async def on_ready(self):
        print('-----')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await bot.change_presence(activity=discord.Game(name=self.status))


def read_token():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    token = os.getenv('DISCORD_BOT_TOKEN')

    if not isinstance(token, str):
        raise FileNotFoundError("Token not found error!")

    return token


if __name__ == '__main__':
    currentpath = os.path.dirname(os.path.abspath(__file__))

    token = read_token()

    with open(currentpath + "/specific_setting.json", encoding='utf-8') as f:
        json_data = json.load(f)

    bot = MyBot(command_prefix=commands.when_mentioned_or('/'))
    bot.run(token)
