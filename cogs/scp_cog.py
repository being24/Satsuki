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


class SCPArticleCog(commands.Cog, name='SCPコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.article_mng = ArticleManager()
        self.c = CommonUtil()

        self.root_url = 'http://scp-jp.wikidot.com/'

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

        if matched_num := number_match.match(num_brt):
            number = matched_num.group()
            brt = num_brt.replace(number, "")
            if brt == '':
                brt = 'en'
            return number, brt
        else:
            return None, None

    async def get_one_SCParticle_data_by_fullname(self, number: str, brt: str) -> Union[None, SCPArticleDatacls]:
        """数字と支部tagから該当する記事のデータを返す関数。複数ヒット時は数字が一致するものを返す

        Args:
            number (str): fullnameの数字
            brt (str): 支部tag

        Returns:
            Union[None, SCPArticleDatacls]: あればSCPArticleDatacls 無ければNone
        """
        data = None

        result = await self.article_mng.get_data_from_fullname_and_tag(
            fullname=number, tags=[brt, 'scp'])

        if result is None:
            return None
        elif len(result) >= 2:
            for i in result:
                if number == re.sub(r'\D', '', i.fullname):
                    data = i
        else:
            data = result[0]

        return data

 
    @commands.group(invoke_without_command=True, description='SCP記事を検索するコマンド')
    async def scp(self, ctx, num_brt: str):
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
                await ctx.send(f'{data.metatitle}\n{self.root_url}{data.fullname}')
            return

    @scp.command(description='SCP記事を検索するコマンド', aliases=['-d'])
    async def detail(self, ctx, num_brt):
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


def setup(bot):
    bot.add_cog(SCPArticleCog(bot))
