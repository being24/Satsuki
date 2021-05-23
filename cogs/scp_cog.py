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

    async def create_detail_embed(self, data: SCPArticleDatacls) -> discord.Embed:
        """詳細をembedにする関数、tzとか文字数制限とかはよしなにしてくれる

        Args:
            data (SCPArticleDatacls): 記事データ

        Returns:
            discord.Embed: 色々調整したデータ
        """
        tags = (' ').join(data.tags)
        created_at = pytz.utc.localize(data.created_at)
        created_at_jst = created_at.astimezone(
            pytz.timezone(self.local_timezone.zone))
        if len(data.metatitle) > 250:
            metatitle = f"{data.metatitle[:250]}{'...'}"
        else:
            metatitle = data.metatitle
        embed = discord.Embed(
            title=f"{metatitle}",
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

    @commands.group(description='TALE記事を検索するコマンド')
    async def tale(self, ctx, word: str):
        """引数からtaleを検索するコマンド"""

        if ctx.invoked_subcommand is None:
            data_list = await self.article_mng.get_data_from_all_and_tag(all=word, tags=['tale'])

            if data_list is None:
                msg = await ctx.reply("該当するtaleは見つかりませんでした")
                await self.c.autodel_msg(msg=msg)
                return

            if (len_of_data := len(data_list)) > 30:
                msg = await ctx.reply(f"ヒット{len_of_data}件、多すぎます")
                await self.c.autodel_msg(msg=msg)
                return

            elif len_of_data == 1:
                data = data_list[0]
                await ctx.send(f'{data.title}\n{self.root_url}{data.fullname}')
                return

            else:
                embed = discord.Embed(
                    title="TALE検索結果",
                    description=f"検索ワード'{word}'にヒットしたTaleは{len_of_data}件です",
                    color=0xff8000)

                for data in data_list:
                    embed.add_field(
                        name=data.title,
                        value=f'{self.root_url}{data.fullname}\nAuthor : {data.created_by}',
                        inline=False)

                embed.set_footer(text="タイトル、URL、著者名から検索しています")
                await ctx.send(embed=embed)
                return

    # サブコマンドでtitile 著者 URL -d を作るべし

    """
    複数→従来通り
    一個→シンプル
    -dオプション→複数個あったら提示して一個に絞って詳細版
                 一個ならそのまま詳細版
    """


def setup(bot):
    bot.add_cog(SCPArticleCog(bot))
