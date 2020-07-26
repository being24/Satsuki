"""
dispander

Copyright (c) 2020 1ntegrale9

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""


from discord import Embed
from discord.ext import commands
import re

regex_discord_message_url = (
    'https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
)


class ExpandDiscordMessageUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.dispand(message)

    async def dispand(self, message):
        messages = await self.extract_messsages(message)
        for m in messages:
            try:
                if message.content:
                    await message.channel.send(embed=self.compose_embed(m))
                for embed in m.embeds:
                    await message.channel.send(embed=embed)
            except BaseException:
                pass

    async def extract_messsages(self, message):
        messages = []
        for ids in re.finditer(regex_discord_message_url, message.content):
            msg_guild = self.bot.get_guild(int(ids['guild']))
            if msg_guild is None:
                await message.channel.send("サーバに入室していません")
                return []
            fetched_message = await self.fetch_message_from_id(
                guild=msg_guild,
                channel_id=int(ids['channel']),
                message_id=int(ids['message']),
            )
            if fetched_message is None:
                await message.channel.send("閲覧許可がありません")
                return []
            messages.append(fetched_message)
        return messages

    @staticmethod
    async def fetch_message_from_id(guild, channel_id, message_id):
        channel = guild.get_channel(channel_id)
        try:
            message = await channel.fetch_message(message_id)
            return message
        except Exception:
            return None

    @staticmethod
    def compose_embed(message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url,
        )
        embed.set_footer(
            text=message.channel.name,
            icon_url=message.guild.icon_url,
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(
                url=message.attachments[0].proxy_url
            )
        return embed


def setup(bot):
    bot.add_cog(ExpandDiscordMessageUrl(bot))
