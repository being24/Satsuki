# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import json
import logging.config
import os
import sys
import traceback

import discord
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=None)

        self.INITIAL_COGS = [
            'cogs.scp_cog',
            'cogs.common_cog',
            'cogs.src_cog',
            'cogs.admin_cog',
            'cogs.dispander',
        ]

        for cog in self.INITIAL_COGS:
            try:
                self.load_extension(cog)
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
        logging.info('rebooted')
        await bot.change_presence(activity=discord.Game(name=self.status))


def read_token():
    file = currentpath + "/token"
    try:
        for line in open(file, 'r'):
            temp = line.replace(" ", "").strip().split("=")
            token = temp[1]
    except FileNotFoundError:
        print("ファイルが見つかりません・・・。")
        print(sys.exc_info())

    return token


if __name__ == '__main__':
    currentpath = os.path.dirname(os.path.abspath(__file__))

    token = read_token()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.FileHandler(
        currentpath + "/data/log/logger.log", 'a', 'utf-8')
    formatter = logging.Formatter(
        '%(levelname)s : %(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    with open(currentpath + "/specific_setting.json", encoding='utf-8') as f:
        json_data = json.load(f)

    bot = MyBot(command_prefix=json_data['command_prefix'])
    bot.run(token)
