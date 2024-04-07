import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

from .utils.ayame_client import (
    AyameClient,
    AyameSearchCountQuery,
    AyameSearchQuery,
)
from .utils.common import CommonUtil
from .utils.paginator import Paginator

logger = logging.getLogger("discord")


class SearchArticleCog(commands.Cog, name="SRCコマンド"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.ayame = AyameClient()
        self.c = CommonUtil()

        self.branches = [
            "en",
            "jp",
            "ru",
            "ko",
            "cn",
            "fr",
            "pl",
            "es",
            "th",
            "de",
            "it",
            "ua",
            "pt",
            "sc",
            "zh",
            "vn",
        ]

        self.object_classes = [
            "safe",
            "euclid",
            "keter",
            "thaumiel",
            "neutralized",
            "explained",
            "apollyon",
            "archon",
            "decommissioned",
            "pending",
            "esoteric-class",
        ]

    @app_commands.command(name="search", description="記事を検索するコマンド")
    async def search(
        self,
        interaction: discord.Interaction,
        word: str | None = None,
        tag1: str | None = None,
        tag2: str | None = None,
        tag3: str | None = None,
        author: str | None = None,
        scp: bool = False,
        tale: bool = False,
        proposal: bool = False,
        joke: bool = False,
        guide: bool = False,
        goi: bool = False,
        explained: bool = False,
        essay: bool = False,
        author_page: bool = False,
        detail: bool = True,
    ):
        """記事を検索するコマンド

        Args:
            word (str, optional): 検索する単語.
            tag1 (str, optional): タグ1.
            tag2 (str, optional): タグ2.
            tag3 (str, optional): タグ3.
            author (str, optional): 著者.
            scp (bool, optional): SCPのみを検索するか.
            tale (bool, optional): Taleのみを検索するか.
            proposal (bool, optional): 提言のみを検索するか.
            joke (bool, optional): ジョークのみを検索するか.
            guide (bool, optional): ガイドのみを検索するか.
            goi (bool, optional): GoIFのみを検索するか.
            explained (bool, optional): explainedのみを検索するか.
            essay (bool, optional): エッセイのみを検索するか.
            author_page (bool, optional): 著者ページのみを検索するか.s
            detail (bool, optional): 詳細を表示するか.
        """

        await interaction.response.defer()

        # tag1, tag2, tag3をリストにまとめる
        tags = [tag1, tag2, tag3]

        # Noneを削除
        tags = [tag for tag in tags if tag is not None]

        if scp:
            tags.append("scp")

        if tale:
            tags.append("tale")

        if proposal:
            tags.append("001提言")

        if joke:
            tags.append("ジョーク")

        if guide:
            tags.append("ガイド")

        if goi:
            tags.append("goi-format")

        if explained:
            tags.append("explained")

        if essay:
            tags.append("エッセイ")

        if author_page:
            tags.append("著者ページ")

        # get search count
        query = AyameSearchCountQuery(
            title=word,
            tags=tags,
            author=author,
            rate_min=None,
            rate_max=None,
            date_from=None,
            date_to=None,
        )

        result_count = await self.ayame.search_complex_count(query)

        if result_count == 0:
            await interaction.followup.send("該当する記事が見つかりません")
            return

        query = AyameSearchQuery(
            title=word,
            tags=tags,
            author=author,
            rate_min=None,
            rate_max=None,
            date_from=None,
            date_to=None,
            page=None,
            show=None,
        )

        # 一個だけならそのまま取得、表示
        if result_count == 1:
            results = await self.ayame.search_complex(query)

            if detail:
                embeds = self.c.create_detail_embed(results[0])
                await interaction.followup.send(embed=embeds)
            else:
                title = self.c.select_title(results[0])
                url = f"http://scp-jp.wikidot.com/{results[0].fullname}"
                await interaction.followup.send(f"{title}\n{url}")
            return

        elif result_count > 200:
            await interaction.followup.send(
                f"{result_count}件見つかりました, 200件以下に絞ってください."
            )
            return

        await interaction.followup.send(f"{result_count}件見つかりました")

        # 全部取得する
        # query.showの最大は100なので、100ずつ取得していく
        results = []

        for i in range(1, result_count, 100):
            query.show = 100
            query.page = i

            res = await self.ayame.search_complex(query)
            results.extend(res)

        ctx = await self.bot.get_context(interaction)

        results_len = len(results)

        embeds = discord.Embed(
            title="該当する記事は以下の通りです",
            description=f"{results_len}件ヒット",
            color=discord.Color.darker_grey(),
        )

        for data in results:
            embeds.add_field(
                name=self.c.select_title(data),
                value=f"http://scp-jp.wikidot.com/{data.fullname}\nAuthor : {data.created_by_unix}",
                inline=False,
            )

        pager = Paginator(ctx=ctx, embed=embeds, field_threshold=10)

        await pager.start()

        # await self.start_paginating(ctx, results)

    @app_commands.command(name="random", description="ランダムな記事を表示するコマンド")
    async def random(self, interaction: discord.Interaction):
        """ランダムな記事を表示するコマンド"""

        await interaction.response.defer()

        results = []

        while results == []:
            branch = random.choice(self.branches)
            object_class = random.choice(self.object_classes)

            query = AyameSearchQuery(
                title=None,
                tags=[object_class, branch, "scp"],
                author=None,
                rate_min=None,
                rate_max=None,
                date_from=None,
                date_to=None,
                show=None,
                page=None,
            )

            results = await self.ayame.search_complex(query)

        result = random.choice(results)

        embed = self.c.create_detail_embed(result)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SearchArticleCog(bot))
