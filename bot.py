# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
import json
import logging
import os
import traceback
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=None)

        for cog in os.listdir(currentpath + "/cogs"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f'cogs.{cog[:-3]}')
                except Exception:
                    traceback.print_exc()

        with open(currentpath + "/data/setting.json", encoding='utf-8') as f:
            self.json_data = json.load(f)

        self.admin_id = self.json_data['admin']["id"]
        self.status = self.json_data['status']
        self.meeting_addr = self.json_data['regular_meeting_addr']

    async def on_ready(self):
        print('-----')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        logging.warning('rebooted')
        await bot.change_presence(activity=discord.Game(name=self.status))


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    token = os.getenv('DISCORD_BOT_TOKEN')
    dsn = os.getenv('SENTRY_DSN')

    if token is None:
        raise FileNotFoundError("Token not found error!")
    if dsn is None:
        raise FileNotFoundError("dsn not found error!")

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s')
    logging.disable(logging.INFO)

    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.WARNING  # Send errors as events
    )

    currentpath = os.path.dirname(os.path.abspath(__file__))

    bot = MyBot(command_prefix=commands.when_mentioned_or('/'))
    with open(currentpath + "/data/specific_setting.json", encoding='utf-8') as f:
        json_data = json.load(f)

    use_sentry(
        bot,
        dsn=dsn,
        integrations=[AioHttpIntegration(), sentry_logging]
    )
    bot.run(token)
