# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import html
import os
import random
import re
import typing
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

import discord
import feedparser
import html2text
# import numpy as np
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from more_itertools import divide

from cogs.utils.common import CommonUtil


@dataclass
class ReserveData:
    draft_title: str
    draft_link: str
    author_name: str
    reserve_time: datetime


@dataclass
class RssData:
    title: str
    link: str
    published_time: datetime
    author: str
    content: str


def shape_content_to_discord(content: str) -> str:
    content = content.replace("<p>", "\n")
    content = content.replace("</p>", "\n")
    content = content.replace("</div>", "")

    content = content.replace("<br />", "\n")

    if '<span class="rt">' in content:  # ルビ
        siz0_0 = content.find('<span class="rt">')
        siz0_1 = content.find('</span>', siz0_0 + 1)
        content = content.replace('<span class="rt">', " - [")
        content = content.replace('</span></span>', "]")  # 多分ここ違う

    if '<strong>' in content:  # 強調
        content = content.replace('<strong>', "**")
        content = content.replace('</strong>', "**")

    if '<span style="text-decoration: content-through;">' in content:  # 取り消し
        content = content.replace(
            '<span style="text-decoration: content-through;">', "~~")
        content = content.replace('</span>', "~~ ", 1)

    if '<span style="text-decoration: undercontent;">' in content:  # 下線
        content = content.replace(
            '<span style="text-decoration: undercontent;">', "__")
        content = content.replace('</span>', "__ ", 1)

    if '<em>' in content:  # 斜体
        content = content.replace('<em>', "*")
        content = content.replace('</em>', "*")

    if 'href' in content:
        match = re.findall(r'href=[\'"]?([^\'" >]+)', content)
        if len(match) == 0:
            content = ""
        elif "javascript" in match[0]:
            content = ""

        if len(match) != 0:
            deco_f = ' ['
            deco_b = f"]({match[0]}) "

        p = re.compile(r"<[^>]*?>")
        content = p.sub(f"{deco_b}", content)
        content = content.replace(deco_b, deco_f, 1)

    content = html.unescape(content)
    # result.append(content)

    return content


class CritiqueCog(commands.Cog, name='批評定例会用コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://scp-jp.wikidot.com"
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.c = CommonUtil()

    @staticmethod
    def from_struct_time_to_datetime(struct_time: str):
        postdate = datetime.strptime(struct_time, "%a, %d %b %Y %H:%M:%S %z")
        postdate = postdate.astimezone()
        return postdate

    def get_content_from_rss(self, target: str) -> List[RssData]:
        feed_data = feedparser.parse(target)
        scp_rss: List[RssData] = []
        for entry in feed_data.entries:
            content = html2text.html2text(str(entry["content"][0]['value']))
            content = content.replace(')', ') ')
            content = content.replace('-\n', '-')
            data = RssData(
                title=str(entry['title']),
                link=str(entry['link']),
                published_time=self.from_struct_time_to_datetime(str(entry['published'])),
                author=str(entry['wikidot_authorname']),
                content=content)
            scp_rss.append(data)
        return scp_rss

    @ commands.command(aliases=['df'], description='本日の下書き予約を表示します')
    @ commands.has_permissions(kick_members=True)
    async def draft(self, ctx, num: typing.Optional[int] = 0):
        """本日の下書き予約を表示します.引数に数字を与えるとその下書き予約を表示します."""
        target_url = 'http://njr-sys.net/irc/draftReserve/'

        d_today = (datetime.now() + timedelta(hours=-3)).date()
        d_today = '2019-10-12'
        response = requests.get(target_url + str(d_today))

        soup = BeautifulSoup(response.text, "html.parser")

        limen_time = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')

        table = soup.find(class_='irc-table zebra-table')
        reserve_list = table.find_all('tr')
        zero_time = datetime.fromtimestamp(0)

        ReserveData_list: List[ReserveData] = []
        for elements in reserve_list:
            author_name = 'None'
            draft_title = 'None'
            draft_link = 'None'
            reserve_time = zero_time
            for element in elements:
                if len(element.string) == 1:
                    pass
                elif '[link]' in element.string:
                    draft_link = element.find('a').get(
                        'href').replace('\n', '')
                    if draft_link is None:
                        draft_link = 'None'
                elif 'wrap irc-table__message' in str(element):
                    if re.search(
                        r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',
                            element.string):
                        reserve_time = datetime.strptime(
                            f'{d_today}-{element.string.replace(" ", "")}', '%Y-%m-%d-%H:%M:%S')
                    else:
                        author_name = element.string
                        if author_name is None:
                            author_name = 'None'
                else:
                    draft_title = element.string
                    if draft_title is None:
                        draft_title = 'None'

            if reserve_time >= limen_time:
                data = ReserveData(
                    author_name=author_name,
                    draft_title=draft_title,
                    draft_link=draft_link,
                    reserve_time=reserve_time)
                ReserveData_list.append(data)

        if len(ReserveData_list) == 0:
            await ctx.send("本日の予約はありません")
            return

        title_message = "下書き批評予約システムからデータを取得します"

        if num == 0:
            embed = discord.Embed(
                title=title_message,
                description=f"本日の下書き批評予約は全{len(ReserveData_list)}件です",
                color=0xff0080)

            for num, data in enumerate(ReserveData_list):
                embed.add_field(
                    name=data.author_name,
                    value=f'{num+1} : [{data.draft_title}]({data.draft_link})\tat: {data.reserve_time}',
                    inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title=title_message,
                description=f"{num}/{len(ReserveData_list)}件目の下書きです",
                color=0xff0080)
            num = num - 1
            data = ReserveData_list[num]
            embed.add_field(
                name=data.author_name,
                value=f'{num+1} : [{data.draft_title}]({data.draft_link})\tat: {data.reserve_time}',
                inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

    @ commands.command(aliases=['mt'])
    @ commands.has_permissions(kick_members=True)
    async def meeting(self, ctx):
        contentlist = self.get_content_from_rss(self.bot.meeting_addr)
        data = contentlist[0]

        embed = discord.Embed(
            title="本日の定例会テーマのお知らせです",
            url=data.link,
            color=0x0000a0)

        if len(data.content) >= 1000:
            content = f'{data.content[:1000]}...'
        else:
            content = data.content

        embed.set_author(name=f'published by {data.author}')

        embed.add_field(
            name=data.title,
            value=content,
            inline=False)

        published_time = data.published_time.strftime('%Y-%m-%d %H:%M:%S')
        embed.set_footer(text=f'published at {published_time}')

        await ctx.send(embed=embed)

    @ commands.command(aliases=['res'])  # 設定でdfの先を変更できるようにする
    # @ commands.dm_only()
    async def reserve(self, ctx, title: str, url: str):
        if not 'Saturday' == datetime.today().strftime('%A'):
            msg = await ctx.reply('今日は土曜日では無いため、予約を受け付けません')
            await self.c.autodel_msg(msg)
            return

        match_url = re.match(
            r"https?://scp-jp-sandbox3\.wikidot\.com/[\w/:%#\$&\?\(\)~\.=\+\-]+", url)
        if not match_url:
            raise commands.BadArgument

        pass

    @ reserve.error
    async def reserve_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            msg = await ctx.reply('このコマンドはDMで実行してください')
            await self.c.autodel_msg(msg)
        elif isinstance(error, commands.MissingRequiredArgument):
            msg = await ctx.reply('引数が足りません')
            await self.c.autodel_msg(msg)
        elif isinstance(error, commands.BadArgument):
            msg = await ctx.reply('第二引数に不正な文字列が入力されています、urlをそのまま張り付けてください')
            await self.c.autodel_msg(msg)

    @ commands.command(aliases=['sh'])
    @ commands.has_permissions(kick_members=True)
    async def shuffle(self, ctx, num: int = 2):
        settime = 10.0 * 60
        reaction_member = []
        emoji_in = '\N{THUMBS UP SIGN}'
        emoji_go = '\N{NEGATIVE SQUARED CROSS MARK}'

        embed = discord.Embed(title="下書き批評に参加するメンバーを募集します", colour=0x1e90ff)
        embed.add_field(
            name=f"参加する方はリアクション{emoji_in}を押してください",
            value="ご参加お待ちしております",
            inline=True)
        embed.set_footer(text='少し待ってからリアクションをつけてください')

        msg = await ctx.reply(embed=embed)

        await msg.add_reaction(emoji_in)
        await msg.add_reaction(emoji_go)
        await asyncio.sleep(0.3)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=settime)
            except asyncio.TimeoutError:
                timeout = await ctx.reply('タイムアウトしました')
                await self.c.autodel_msg(msg=timeout)
                break
            else:
                if str(reaction.emoji) == emoji_go:
                    if ctx.author.id == user.id:
                        if len(reaction_member) < num:
                            await ctx.send('最低人数を満たしませんでした')
                            await msg.clear_reactions()
                            break

                        await ctx.send('募集を終了しました')

                        reaction_member = list(set(reaction_member))

                        random.shuffle(reaction_member)
                        divided_reaction_member = list(
                            divide(num, reaction_member))

                        embed = discord.Embed(
                            title="割り振りは以下の通りです",
                            color=0x1e90ff)

                        for i in range(num):
                            str_member = '\n'.join(divided_reaction_member[i])
                            embed.add_field(
                                name=f'group:{i}', value=f'{str_member}', inline=True)
                        embed.set_footer(text='よろしくお願いします')

                        await msg.edit(embed=embed)
                        await msg.clear_reactions()

                        break
                    else:
                        await msg.remove_reaction(str(reaction.emoji), user)

                elif str(reaction) == emoji_in:
                    if user.id in reaction_member:
                        pass
                    else:
                        reaction_member.append(user.mention)


def setup(bot):
    bot.add_cog(CritiqueCog(bot))
