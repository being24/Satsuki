# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
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
        super().__init__(command_prefix, help_command=None, intents=intents)

        for cog in os.listdir(root_path / "cogs"):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f'cogs.{cog[:-3]}')
                except Exception:
                    traceback.print_exc()

        with open(root_path / "data/setting.json", encoding='utf-8') as f:
            self.json_data = json.load(f)

        self.status = self.json_data['status']
        self.meeting_addr = self.json_data['regular_meeting_addr']

        self.root_url = 'http://scp-jp.wikidot.com/'

    async def on_ready(self):
        print('-----')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        logging.warning('rebooted')
        await bot.change_presence(activity=discord.Game(name=self.status))


if __name__ == '__main__':
    root_path = pathlib.Path(__file__).parents[0]

    dotenv_path = root_path / '.env'

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

    intents = discord.Intents.default()
    intents.members = True
    intents.typing = False

    bot = MyBot(command_prefix=commands.when_mentioned_or('/'))

    use_sentry(
        bot,
        dsn=dsn,
        integrations=[AioHttpIntegration(), sentry_logging]
    )
    bot.run(token)
