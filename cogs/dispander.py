"""
dispander

Copyright (c) 2020 1ntegrale9

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
"""
import re

from discord import Embed
from discord.ext import commands

from cogs.utils.setting_manager import SettingManager
from cogs.utils.common import CommonUtil

regex_discord_message_url = (
    'https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{18,21})/(?P<channel>[0-9]{18,21})/(?P<message>[0-9]{18,21})'
)


class ExpandDiscordMessageUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setting_mng = SettingManager()
        self.c = CommonUtil()

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
            except BaseException as e:
                raise

    async def extract_messsages(self, message):
        messages = []
        for ids in re.finditer(regex_discord_message_url, message.content):
            # 同一ならTrue、片方がFalseならFalse
            # ここで判定入れる
            url_guild_id = int(ids['guild'])
            msg_guild = self.bot.get_guild(url_guild_id)
            if msg_guild is None:
                msg = await message.channel.send("サーバに入室していません")
                await self.c.autodel_msg(msg=msg)
                return []

            """
            if message.guild.id == url_guild_id:  # 同一サーバー内ならOK
                pass
            else:  # 同一サーバー内でなくて、どちらかがFalseならFalse(NAND)
                if not (await self.setting_mng.is_dispand(message.guild.id) and await self.setting_mng.is_dispand(url_guild_id)):
                    msg = await message.channel.send("送信が許可されていません")
                    await self.c.autodel_msg(msg=msg)
                    return []
            """

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
        channel = guild.get_channel_or_thread(channel_id)
        if channel is None:
            channel = await guild.fetch_channel(channel_id)
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

        if message.author.avatar is None:
            avatar_url = 'https://cdn.discordapp.com/embed/avatars/0.png'
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
            embed.set_image(
                url=message.attachments[0].proxy_url
            )
        return embed

    @commands.command(description='dispandの状態確認関数')
    @commands.has_permissions(manage_guild=True)
    async def show_dispand(self, ctx):
        """サーバー間でのメッセージ展開が有効かどうかを確認する関数。サーバー管理権限が必要"""
        footer_word = '\nサーバー間展開を使用するためには、双方のサーバーが展開を許可している必要があります'
        if await self.setting_mng.is_dispand(ctx.guild.id):
            await ctx.reply(f'本サーバーのメッセージ展開は許可されています{footer_word}')
        else:
            await ctx.reply(f'本サーバーのメッセージ展開は許可されていません{footer_word}')

    @commands.command(description='dispandを制御する関数')
    @commands.has_permissions(manage_guild=True)
    async def set_dispand(self, ctx, tf: bool):
        """サーバー間でのメッセージ展開を制御する関数。サーバー管理権限が必要"""
        await self.setting_mng.set_dispand(ctx.guild.id, tf)
        await ctx.reply(f'メッセージ展開設定を{tf}に設定しました')


def setup(bot):
    bot.add_cog(ExpandDiscordMessageUrl(bot))
