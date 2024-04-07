"""
dispander

Copyright (c) 2020 1ntegrale9
Copyright (c) 2021 being24
Copyright (c) 2024 r74tech

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""

import logging
import re

import discord
from discord import Embed
from discord.ext import commands

from cogs.utils.common import CommonUtil

logger = logging.getLogger("discord")


regex_discord_message_url = (
    "https://(ptb.|canary.)?discord(app)?.com/channels/"
    "(?P<guild>[0-9]{18,21})/(?P<channel>[0-9]{18,21})/(?P<message>[0-9]{18,21})"
)


class ExpandDiscordMessageUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.c = CommonUtil()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.dispand(message)

    async def dispand(self, message: discord.Message):
        messages = await self.extract_messages(message)
        for m in messages:
            try:
                if message.content:
                    await message.channel.send(embed=self.compose_embed(m))
                for embed in m.embeds:
                    await message.channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(
                    f"Forbidden: {message.guild.name} {message.channel.name}"
                )

    async def extract_messages(self, message: discord.Message):
        messages = []
        for ids in re.finditer(regex_discord_message_url, message.content):
            url_guild_id = int(ids["guild"])
            msg_guild = self.bot.get_guild(url_guild_id)
            if msg_guild is None:
                await message.channel.send("サーバに入室していません", delete_after=5)
                return []

            fetched_message = await self.fetch_message_from_id(
                guild=msg_guild,
                channel_id=int(ids["channel"]),
                message_id=int(ids["message"]),
            )
            if fetched_message is None:
                await message.channel.send("閲覧許可がありません")
                return []
            messages.append(fetched_message)
        return messages

    @staticmethod
    async def fetch_message_from_id(
        guild: discord.Guild, channel_id: int, message_id: int
    ):
        channel = guild.get_channel_or_thread(channel_id)
        if channel is None:
            channel = await guild.fetch_channel(channel_id)
        try:
            message = await channel.fetch_message(message_id)
            return message
        except Exception:
            return None

    @staticmethod
    def compose_embed(message: discord.Message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
        )

        if message.author.avatar is None:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        else:
            avatar_url = message.author.avatar.replace(format="png").url

        embed.set_author(
            name=message.author.display_name,
            icon_url=avatar_url,
        )
        embed.set_footer(
            text=message.channel.name,
            icon_url=message.guild.icon.url,
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(url=message.attachments[0].proxy_url)
        return embed


async def setup(bot):
    await bot.add_cog(ExpandDiscordMessageUrl(bot))
