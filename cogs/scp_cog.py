# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import typing
from typing import List, Tuple, Union

import discord
import mojimoji
import pytz
import tzlocal
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages

from .utils.article_manager import ArticleManager, SCPArticleDatacls
from .utils.common import CommonUtil

number_match = re.compile(r'(?<![0-9])\d{3,4}(?![0-9])')  # 3か4桁のものだけマッチ


class SearchPager(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=10)
        self.root_url = 'http://scp-jp.wikidot.com/'
        self.c = CommonUtil()

    async def write_page(self, menu, fields: List[SCPArticleDatacls] = []) -> discord.Embed:
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = discord.Embed(
            title="検索結果は以下の通りです",
            description=f"{len_data}件ヒット",
            color=discord.Color.darker_grey())

        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} records.")

        for data in fields:
            embed.add_field(
                name=self.c.select_title(data),
                value=f'{self.root_url}{data.fullname}\nAuthor : {data.created_by}',
                inline=False)

        return embed

    async def format_page(self, menu, entries):

        return await self.write_page(menu, entries)


class SCPArticleCog(commands.Cog, name='SCPコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.article_mng = ArticleManager()
        self.c = CommonUtil()

        self.root_url = 'http://scp-jp.wikidot.com/'

    async def start_paginating(self, ctx, data_list: List[SCPArticleDatacls]):
        menu = MenuPages(source=SearchPager(ctx, data_list),
                         delete_message_after=False,
                         clear_reactions_after=True,
                         timeout=60.0)
        await menu.start(ctx)

    async def send_message(self, ctx, data_list: Union[List[SCPArticleDatacls], None]) -> None:
        if data_list is None:
            msg = await ctx.reply("該当するページは見つかりませんでした")
            await self.c.autodel_msg(msg=msg)
            return

        elif len(data_list) == 1:
            data = data_list[0]
            title = self.c.select_title(data)
            await ctx.send(f'{title}\n{self.bot.root_url}{data.fullname}')
            return

        else:
            await self.start_paginating(ctx, data_list)
            return

    def prosess_arg(self, num_brt: str) -> tuple:
        """引数を処理して、数字とbrtに分離する関数

        Args:
            num_brt (str): 引数

        Returns:
            tuple: 数字のbrtのtuple 失敗したらNoneになる
        """
        num_brt = num_brt.casefold()
        num_brt = mojimoji.zen_to_han(num_brt)
        num_brt = num_brt.replace(" ", "").replace("-", "").replace("scp", "")

        if matched_num := number_match.search(num_brt):
            number = matched_num.group()
            brt = num_brt.replace(number, "")
            if brt == '':
                brt = 'en'
            return number, brt
        else:
            return None, None

    async def get_one_SCParticle_data_by_fullname(self, number: str, brt: str) -> Union[None, SCPArticleDatacls]:
        """数字と支部tagから該当する記事のデータを返す関数。複数ヒット時は数字が一致し、より新しいものを返す

        Args:
            number (str): fullnameの数字
            brt (str): 支部tag

        Returns:
            Union[None, SCPArticleDatacls]: あればSCPArticleDatacls 無ければNone
        """
        data = None
        exclusion_list = ['ジョーク', '001提言']  # この実装嫌

        result = await self.article_mng.get_data_from_fullname_and_tag(
            fullname=number, tags=[brt, 'scp'])

        if result is None:
            return None
        elif len(result) >= 2:
            for i in reversed(result):
                if number == re.sub(r'\D', '', i.fullname):
                    if any(
                            exclusion in i.tags for exclusion in exclusion_list):
                        continue
                    else:
                        data = i
        else:
            data = result[0]

        return data

    @commands.group(invoke_without_command=True, description='SCP記事を検索するコマンド')
    async def scp(self, ctx, *, num_brt: str):
        """引数からscpを検索するコマンド-シンプル版"""
        if ctx.invoked_subcommand is None:
            number, brt = self.prosess_arg(num_brt)
            if (number and brt) is None:
                msg = await ctx.reply('入力が正しくありません')
                await self.c.autodel_msg(msg=msg)
                return

            data = await self.get_one_SCParticle_data_by_fullname(number, brt)

            if data is None:
                msg = await ctx.reply('該当する記事が見つかりません')
                await self.c.autodel_msg(msg=msg)
                return
            else:
                title = self.c.select_title(data)
                await ctx.send(f'{title}\n{self.root_url}{data.fullname}')
            return

    @scp.command(description='SCP記事をurlから検索するコマンド', aliases=['-u'])
    async def url_(self, ctx, url: str):
        """urlからtaleを検索するコマンド\n`/scp -u URL`で、そのURLを持つSCP記事を表示します。"""

        data_list = await self.article_mng.get_data_from_url_and_tag(url=url, tags=['scp'])
        await self.send_message(ctx, data_list)

    @scp.command(description='SCP記事を著者から検索するコマンド', aliases=['-a'])
    async def author(self, ctx, author: str):
        """著者からtaleを検索するコマンド\n`/scp -a 著者名`で、その人が著者のSCP記事を表示します。"""

        data_list = await self.article_mng.get_data_from_author_and_tag(author=author, tags=['scp'])
        await self.send_message(ctx, data_list)

    @scp.command(description='SCP記事をタイトルから検索するコマンド', aliases=['-t'])
    async def title(self, ctx, title: str):
        """タイトルからtaleを検索するコマンド\n`/scp -t タイトル`で、そのタイトルを持つSCP記事を表示します。"""

        data_list = await self.article_mng.get_data_from_title_and_tag(title=title, tags=['scp'])
        await self.send_message(ctx, data_list)

    @scp.command(description='SCP記事を検索するコマンド', aliases=['-d'])
    async def detail(self, ctx, *, num_brt: str):
        """引数からscpを検索するコマンド-複雑版"""
        number, brt = self.prosess_arg(num_brt)
        if (number and brt) is None:
            msg = await ctx.reply('入力が正しくありません')
            await self.c.autodel_msg(msg=msg)
            return

        data = await self.get_one_SCParticle_data_by_fullname(number, brt)

        if data is None:
            msg = await ctx.reply('該当する記事が見つかりません')
            await self.c.autodel_msg(msg=msg)
            return
        else:
            embed = self.c.create_detail_embed(data)
            await ctx.send(embed=embed)

        return

    @commands.command(description='ランダムにSCPタグつき記事を表示するコマンド')
    async def rand(self, ctx, brt: str = 'all'):
        """`/rand 支部タグ`でそのタグのついているSCPからランダムに表示します。引数無しで全支部指定です\n工夫すると別の使い方もできるかも"""
        brt = brt.lower()

        data = await self.article_mng.get_scp_random(brt)

        if data is None:
            msg = await ctx.reply(f'{brt}タグは存在しません')
            await self.c.autodel_msg(msg=msg)
        else:
            embed = self.c.create_detail_embed(data)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SCPArticleCog(bot))
