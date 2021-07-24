# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import html
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import aiohttp
import discord
import feedparser
import html2text
import pytz
import tzlocal
from bs4 import BeautifulSoup
from discord.ext import commands
from more_itertools import divide

from cogs.utils.common import CommonUtil
from cogs.utils.meeting_manager import MeetingManager, ReserveData


@dataclass
class RssData:
    title: str
    link: str
    published_time: datetime
    author: str
    content: str


class CritiqueCog(commands.Cog, name='批評定例会用コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://scp-jp.wikidot.com"

        self.local_timezone = tzlocal.get_localzone()

        self.c = CommonUtil()
        self.meeting_mng = MeetingManager()

    @staticmethod
    def from_struct_time_to_datetime(struct_time: str) -> Optional[datetime]:
        """wikidot-RSSの文字列をdatetimeに変換する

        Args:
            struct_time (str): RSSの文字列

        Returns:
            Optional[datetime]: awareなdatetime
        """

        try:
            postdate = datetime.strptime(
                struct_time, "%a, %d %b %Y %H:%M:%S %z")
            postdate = postdate.utcnow()
            return postdate
        except ValueError:
            return None

    async def get_content_from_rss(self, target: str) -> List[RssData]:
        """RSSのデータをパース、RssDataに変換して返す関数

        Args:
            target (str): RSSのデータ

        Returns:
            List[RssData]: RSSのデータクラス
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(target) as r:
                if r.status == 200:
                    response = await r.text()
                else:
                    raise

        feed_data = feedparser.parse(response)
        scp_rss: List[RssData] = []

        for entry in feed_data.entries:
            content = html2text.html2text(str(entry["content"][0]['value']))
            content = content.replace(')', ') ')
            content = content.replace('-\n', '-')

            published_time = self.from_struct_time_to_datetime(
                str(entry['published']))

            if published_time is None:
                published_time = datetime.fromtimestamp(0)

            data = RssData(
                title=str(entry['title']),
                link=str(entry['link']),
                published_time=published_time,
                author=str(entry['wikidot_authorname']),
                content=content)
            scp_rss.append(data)

        return scp_rss

    def generate_ReserveData(
            self,
            d_today: str,
            response: str) -> List[ReserveData]:
        """取得したソースからReserveDataのリストを生成する関数

        Args:
            d_today (str): 今日の日付（3hずれてる）
            response (str): ソース

        Returns:
            List[ReserveData]: ReserveDataのデータクラス
        """

        soup = BeautifulSoup(response, "html.parser")

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
                if element.string is None:
                    continue
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
                        reserve_time = reserve_time.astimezone(
                            self.local_timezone)
                        reserve_time = reserve_time.astimezone(pytz.utc)

                    else:
                        author_name = element.string
                        if author_name is None:
                            author_name = 'None'
                else:
                    draft_title = html.unescape(element.string)
                    if draft_title is None:
                        draft_title = 'None'

            data = ReserveData(
                msg_id=0,
                author_name=author_name[:50],
                draft_title=draft_title[:50],
                draft_link=draft_link,
                reserve_time=reserve_time)
            ReserveData_list.append(data)
        return ReserveData_list

    async def send_reserve_embed(self, ctx, num: int, list_reservation_available: List[ReserveData]) -> None:
        """予約リストをnumに合わせてembedで送ってくれるやつ

        Args:
            ctx ([type]): いつもの
            num (int): 0なら全部、それ以外なら一つ
            list_reservation_available (List[ReserveData]): 対象のリスト
        """

        title_message = "下書き批評予約システムからデータを取得します"

        if num == 0:
            embed = discord.Embed(
                title=title_message,
                description=f"本日の下書き批評予約は全{len(list_reservation_available)}件です",
                color=0xff0080)

            for num, data in enumerate(list_reservation_available):
                reserve_time_jst = self.c.convert_utc_into_jst(
                    data.reserve_time)

                reserve_time_jst = reserve_time_jst.strftime(
                    '%Y-%m-%d %H:%M:%S')
                embed.add_field(
                    name=data.author_name,
                    value=f'{num+1} : [{data.draft_title}]({data.draft_link})\tat: {reserve_time_jst}',
                    inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

        else:
            if (list_len := len(list_reservation_available)) < num:
                msg = await ctx.reply('指定された数字が大きすぎます')
                await self.c.autodel_msg(msg=msg)
                return

            embed = discord.Embed(
                title=title_message,
                description=f"{num}/{list_len}件目の下書きです",
                color=0xff0080)
            num = num - 1
            data = list_reservation_available[num]
            embed.add_field(
                name=data.author_name,
                value=f'{num+1} : [{data.draft_title}]({data.draft_link})\tat: {data.reserve_time}',
                inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.meeting_mng.create_table()

    @ commands.group(invoke_without_command=True,
                     aliases=['df'], description='本日の下書き予約を表示します')
    @ commands.has_permissions(kick_members=True)
    async def draft(self, ctx, num: int = 0):
        """本日の下書き予約を表示します.引数に数字を与えるとその下書き予約を表示します."""

        utc_time = datetime.utcnow()

        jst_time = self.c.convert_utc_into_jst(utc_time)
        jst_time = jst_time + timedelta(hours=-3)  # 日付をまたぐときがあるのでその対策

        d_today = (jst_time).strftime('%Y-%m-%d')

        """
        d_today = '2019-10-12'  # debug
        jst_time = datetime.strptime(
            f'{d_today}-20:46:00', '%Y-%m-%d-%H:%M:%S')
        jst_time = jst_time.astimezone(self.local_timezone)
        """

        limen_time = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')
        limen_time = self.local_timezone.localize(limen_time)

        if num == 0:
            target_url = 'http://njr-sys.net/irc/draftReserve/'

            async with aiohttp.ClientSession() as session:
                async with session.get(f'{target_url}{d_today}') as r:
                    if r.status == 200:
                        response = await r.text()
                    else:
                        await ctx.send("データ取得に失敗しました")
                        return

            ReserveData_list = self.generate_ReserveData(d_today, response)

            full_reserve_data = await self.meeting_mng.upsert_and_return_reserve_data(jst_time, ReserveData_list)

        else:
            full_reserve_data = await self.meeting_mng.get_reserve_data_from_date(jst_time)

        if full_reserve_data is None:
            await ctx.send("本日の予約はありません")
            return

        list_reservation_available = []
        for data in full_reserve_data:
            reserve_time = self.c.convert_utc_into_jst(data.reserve_time)

            if reserve_time >= limen_time:
                list_reservation_available.append(data)

        if len(list_reservation_available) == 0:
            await ctx.send("本日の予約はありません")
            return

        await self.send_reserve_embed(ctx, num, list_reservation_available)

    @draft.command(description='すべての今日の予約を表示するコマンド', aliases=['-a'])
    async def all(self, ctx, num: int = 0):
        """対象外であっても表示します、一応作成"""
        utc_time = datetime.utcnow()

        jst_time = self.c.convert_utc_into_jst(utc_time)

        d_today = (jst_time + timedelta(hours=-3)
                   ).strftime('%Y-%m-%d')   # 日付をまたぐときがあるのでその対策

        """
        d_today = '2019-10-12'  # debug
        jst_time = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')
        jst_time = jst_time.astimezone(self.local_timezone)
        """

        if num == 0:
            target_url = 'http://njr-sys.net/irc/draftReserve/'

            async with aiohttp.ClientSession() as session:
                async with session.get(f'{target_url}{d_today}') as r:
                    if r.status == 200:
                        response = await r.text()
                    else:
                        await ctx.send("データ取得に失敗しました")
                        return

            ReserveData_list = self.generate_ReserveData(d_today, response)

            full_reserve_data = await self.meeting_mng.upsert_and_return_reserve_data(jst_time, ReserveData_list)

        else:
            full_reserve_data = await self.meeting_mng.get_reserve_data_from_date(jst_time)

        if full_reserve_data is None:
            await ctx.send("本日の予約はありません")
            return

        await self.send_reserve_embed(ctx, num, full_reserve_data)

    @ commands.command(aliases=['res'],
                       description="定例会の予約をするコマンド",
                       hidden=True)
    # @ commands.dm_only()
    async def reserve(self, ctx, title: str, url: str):
        """煮汁の不具合に備えて実装"""
        if ctx.invoked_subcommand is None:
            time = datetime.utcnow()

            time_jst = self.c.convert_utc_into_jst(time)

            match_url = re.match(
                r"https?://scp-jp-sandbox3\.wikidot\.com/[\w/:%#\$&\?\(\)~\.=\+\-]+", url)
            if not match_url:
                raise commands.BadArgument

            name = ctx.message.author.nick
            if name is None:
                name = ctx.message.author.name

            data = ReserveData(
                msg_id=ctx.message.id,
                author_name=name[:50],
                draft_title=title[:50],
                draft_link=url[:100],
                reserve_time=ctx.message.created_at)

            await self.meeting_mng.add_reserve_data(data)
            time_jst = self.c.convert_utc_into_jst(ctx.message.created_at)
            time_jst = time_jst.strftime('%Y-%m-%d %H:%M:%S')
            await ctx.reply(f'{time_jst}に{data.draft_title}ついての予約を受け付けました')

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

    @ commands.command(aliases=['mt'], description="定例会告知用コマンド")
    @ commands.has_permissions(kick_members=True)
    async def meeting(self, ctx):
        """定例会告知スレッドRSSから書き込みを取得、送信するコマンド"""
        contentlist = await self.get_content_from_rss(self.bot.meeting_addr)
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

    @ commands.command(aliases=['sh'], description="リアクションをつけた人を均等に分割するコマンド")
    @ commands.has_permissions(kick_members=True)
    async def shuffle(self, ctx, num: int = 2):
        """あんまり使ってるところを見たことはない"""
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
