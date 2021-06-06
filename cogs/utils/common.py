# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from discord.ext.commands import bot
import pytz
import tzlocal
from cogs.utils.article_manager import SCPArticleDatacls
import typing
import discord


class CommonUtil():
    def __init__(self):
        self.bot = bot
        self.local_timezone = tzlocal.get_localzone()
        self.root_url = 'http://scp-jp.wikidot.com/'

    @staticmethod
    async def autodel_msg(msg: discord.Message, second: int = 5):
        """渡されたメッセージを指定秒数後に削除する関数

        Args:
            msg (discord.Message): 削除するメッセージオブジェクト
            second (int, optional): 秒数. Defaults to 5.
        """
        try:
            await msg.delete(delay=second)
        except discord.Forbidden:
            pass

    @staticmethod
    def return_member_or_role(guild: discord.Guild,
                              id: int) -> typing.Union[discord.Member,
                                                       discord.Role,
                                                       None]:
        """メンバーか役職オブジェクトを返す関数

        Args:
            guild (discord.guild): discordのguildオブジェクト
            id (int): 役職かメンバーのID

        Returns:
            typing.Union[discord.Member, discord.Role]: discord.Memberかdiscord.Role
        """
        user_or_role = guild.get_role(id)
        if user_or_role is None:
            user_or_role = guild.get_member(id)

        return user_or_role

    def create_detail_embed(self, data: SCPArticleDatacls) -> discord.Embed:
        """詳細をembedにする関数、tzとか文字数制限とかはよしなにしてくれる

        Args:
            data (SCPArticleDatacls): 記事データ

        Returns:
            discord.Embed: 色々調整したデータ
        """
        tags = (' ').join(data.tags)

        created_at_jst = self.convert_utc_into_jst(data.created_at)

        title = self.select_title(data)
        title = self.reap_metatitle_to_limit(title)

        embed = discord.Embed(
            title=f"{title}",
            url=f"{self.root_url}{data.fullname}",
            color=0x8f1919)
        embed.add_field(
            name="created_by",
            value=f"{data.created_by}",
            inline=False)
        embed.add_field(
            name="created_at",
            value=f"{created_at_jst.strftime('%Y/%m/%d %H:%M')}",
            inline=False)
        embed.add_field(name="rate", value=f"{data.rating}", inline=True)
        embed.add_field(name="tags", value=f"{tags}", inline=True)

        return embed

    def select_title(self, data: SCPArticleDatacls) -> str:
        """メタタイトルをがあればそちらを、そうでなければtitleを返す関数

        Args:
            data (SCPArticleDatacls)

        Returns:
            str
        """
        if data.metatitle is None:
            title = data.title
        else:
            title = data.metatitle
        return title

    def convert_utc_into_jst(self, time: datetime) -> datetime:
        """naiveなUTCをawareなJSTにする関数

        Args:
            created_at (datetime): naiveなUTC

        Returns:
            datetime: awareなJST
        """
        time = pytz.utc.localize(time)
        created_at_jst = time.astimezone(
            pytz.timezone(self.local_timezone.zone))
        return created_at_jst

    def reap_metatitle_to_limit(self, metatitle: str) -> str:
        """embedのタイトルの文字数制限に合わせるために短くする関数

        Args:
            metatitle (str)

        Returns:
            str
        """
        if len(metatitle) > 250:
            metatitle = f"{metatitle[:250]}{'...'}"
        else:
            metatitle = metatitle
        return metatitle
