# !/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Tuple, Union

import discord
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages

from .utils.article_manager import ArticleManager, SCPArticleDatacls
from .utils.common import CommonUtil


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


class SearchCog(commands.Cog, name='SRCコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.article_mng = ArticleManager()
        self.c = CommonUtil()

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

    @commands.group(invoke_without_command=True,
                    description='全ページを検索するコマンド', aliases=['src'])
    async def search(self, ctx, word: str):
        """引数から全ページを検索するコマンド\n`/src 単語`でその単語を含むページを検索します。"""
        if ctx.invoked_subcommand is None:
            data_list = await self.article_mng.get_data_from_all_ilike(all_=word)

            await self.send_message(ctx, data_list)

    @search.command(description='タグとその他検索', aliases=['-c'], rest_is_raw=True)
    async def complex(self, ctx, *args):
        """ワードとタグで検索するコマンド\n`/src -c オリジナル scp en` と入れるとオリジナルと言う文字列を持つscpとenタグが有るページを検索します"""
        data_list = await self.article_mng.get_data_from_all_and_tag(all_=args[0], tags=args[1:])
        await self.send_message(ctx, data_list)

        pass

    @search.command(description='皐月版複数タグ検索', aliases=['-t'])
    async def tags(self, ctx, *tags):
        """複数のタグで検索するコマンド`/src -t tag1 tag2`でtag1とtag2両方を持つ記事を検索します。\ntag数の上限はありません。"""

        data_list = await self.article_mng.get_data_from_tags_and(tags=tags)
        await self.send_message(ctx, data_list)

    @search.command(description='ページの詳細版を表示するコマンド', aliases=['-d'])
    async def detail(self, ctx, word: str):
        """ページの詳細版を検索するコマンド\n`/src -d 単語`で、その単語を含むページの詳細を表示します\n複数ヒットした場合は通常の一覧表示を行います"""

        data_list = await self.article_mng.get_data_from_all_ilike(all_=word)
        if data_list is None:
            msg = await ctx.reply("該当するページは見つかりませんでした")
            await self.c.autodel_msg(msg=msg)

        elif len(data_list) > 1:
            await self.send_message(ctx, data_list)
            msg = await ctx.reply('複数ヒットしたため、一覧を表示します')
            await self.c.autodel_msg(msg=msg)

        else:
            embed = self.c.create_detail_embed(data_list[0])
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SearchCog(bot))
