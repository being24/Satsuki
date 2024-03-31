import logging
import re

import discord
import mojimoji
from discord import app_commands
from discord.ext import commands

from .utils.ayame_client import AyameClient, AyameSearchQuery
from .utils.common import CommonUtil

number_match = re.compile(r"(?<![0-9])\d{3,4}(?![0-9])")  # 3か4桁のものだけマッチ

logger = logging.getLogger("discord")


class SCPArticleCog(commands.Cog, name="SCPコマンド"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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
        number, brt = self.process_arg(num_brt)
        if (number and brt) is None:
            await interaction.response.send_message(
                "入力が正しくありません", ephemeral=True
            )
            return

        await interaction.response.defer()

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

        if len(result) == 0 or not data:
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
