import re

import discord

import mojimoji
from discord import app_commands
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages

from .utils.ayame_client import AyameClient, AyameSearchQuery, AyameSearchResult
from .utils.common import CommonUtil

number_match = re.compile(r"(?<![0-9])\d{3,4}(?![0-9])")  # 3か4桁のものだけマッチ


# class SearchPager(ListPageSource):
#     def __init__(self, ctx, data):
#         self.ctx = ctx
#         super().__init__(data, per_page=10)
#         self.root_url = "http://scp-jp.wikidot.com/"
#         self.c = CommonUtil()

#     async def write_page(
#         self, menu, fields: List[SCPArticleDatacls] = []
#     ) -> discord.Embed:
#         offset = (menu.current_page * self.per_page) + 1
#         len_data = len(self.entries)

#         embed = discord.Embed(
#             title="検索結果は以下の通りです",
#             description=f"{len_data}件ヒット",
#             color=discord.Color.darker_grey(),
#         )

#         embed.set_footer(
#             text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} records."
#         )

#         for data in fields:
#             embed.add_field(
#                 name=self.c.select_title(data),
#                 value=f"{self.root_url}{data.fullname}\nAuthor : {data.created_by}",
#                 inline=False,
#             )

#         return embed

#     async def format_page(self, menu, entries):
#         return await self.write_page(menu, entries)


class SCPArticleCog(commands.Cog, name="SCPコマンド"):
    def __init__(self, bot):
        self.bot: commands.bot = bot

        self.ayame = AyameClient()
        self.c = CommonUtil()

    def process_arg(self, num_brt: str) -> tuple:
        """引数を処理して、数字とbrtに分離する関数

        Args:
            num_brt (str): 引数

        Returns:
            tuple: 数字とbrtのtuple 失敗したらNoneになる
        """
        num_brt = num_brt.casefold()
        num_brt = mojimoji.zen_to_han(num_brt)
        num_brt = num_brt.replace(" ", "").replace("-", "").replace("scp", "")

        if matched_num := number_match.search(num_brt):
            number = matched_num.group()
            brt = num_brt.replace(number, "")
            if brt == "":
                brt = "en"
            return number, brt
        else:
            return None, None

    @app_commands.command(name="scp", description="SCP記事を検索するコマンド")
    async def scp(
        self, interaction: discord.Interaction, num_brt: str, detail: bool = True
    ):
        await interaction.response.defer()

        number, brt = self.process_arg(num_brt)
        if (number and brt) is None:
            await interaction.response.send_message(
                "入力が正しくありません", ephemeral=True
            )
            return

        query = AyameSearchQuery(
            title=number,
            tags=[brt, "scp"],
            author=None,
            rate_min=None,
            rate_max=None,
            date_from=None,
            date_to=None,
            page=None,
            show=None,
        )

        result = await self.ayame.search_complex(query)

        # resultのtitleから数字だけを正規表現だけで取り出し、numberと一致するものを返す
        if len(result) >= 2:
            for i in reversed(result):
                if number == re.sub(r"\D", "", i.title):
                    data = i
        else:
            data = result[0]

        if data is None:
            await interaction.response.send_message(
                "該当する記事が見つかりません", ephemeral=True
            )
            return

        if not detail:
            title = self.c.select_title(data)
            url = f"http://scp-jp.wikidot.com/{data.fullname}"

            await interaction.followup.send(f"{title}\n{url}")
            return

        embed = self.c.create_detail_embed(data)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SCPArticleCog(bot))
