import logging
import typing

import discord
from discord.ext.commands import bot
from zoneinfo import ZoneInfo

logger = logging.getLogger("discord")


class CommonUtil:
    def __init__(self):
        self.bot = bot
        self.jst_timezone = ZoneInfo("Asia/Tokyo")
        self.root_url = "http://scp-jp.wikidot.com/"

    @staticmethod
    async def delete_after(
        msg: discord.Message | discord.InteractionMessage, second: int = 5
    ):
        """渡されたメッセージを指定秒数後に削除する関数

        Args:
            msg (discord.Message): 削除するメッセージオブジェクト
            second (int, optional): 秒数. Defaults to 5.
        """
        if isinstance(msg, discord.InteractionMessage):
            try:
                await msg.delete(delay=second)
            except discord.Forbidden:
                logger.error("メッセージの削除に失敗しました。Forbidden")
        else:
            try:
                await msg.delete(delay=second)
            except discord.Forbidden:
                logger.error("メッセージの削除に失敗しました。Forbidden")

    # def create_detail_embed(self, data: SCPArticleDatacls) -> discord.Embed:
    #     """詳細をembedにする関数、tzとか文字数制限とかはよしなにしてくれる

    #     Args:
    #         data (SCPArticleDatacls): 記事データ

    #     Returns:
    #         discord.Embed: 色々調整したデータ
    #     """
    #     tags = (" ").join(data.tags)

    #     created_at_jst = self.convert_utc_into_jst(data.created_at)

    #     title = self.select_title(data)
    #     title = self.reap_metatitle_to_limit(title)

    #     embed = discord.Embed(
    #         title=f"{title}", url=f"{self.root_url}{data.fullname}", color=0x8F1919
    #     )
    #     embed.add_field(name="created_by", value=f"{data.created_by}", inline=False)
    #     embed.add_field(
    #         name="created_at",
    #         value=f"{created_at_jst.strftime('%Y/%m/%d %H:%M')}",
    #         inline=False,
    #     )
    #     embed.add_field(name="rate", value=f"{data.rating}", inline=True)
    #     embed.add_field(name="tags", value=f"{tags}", inline=True)

    #     return embed

    # def select_title(self, data: SCPArticleDatacls) -> str:
    #     """メタタイトルをがあればそちらを、そうでなければtitleを返す関数

    #     Args:
    #         data (SCPArticleDatacls)

    #     Returns:
    #         str
    #     """
    #     if data.metatitle is not None:
    #         title = data.metatitle
    #     elif data.title != "":
    #         title = data.title
    #     else:
    #         title = "None"

    #     title = self.reap_metatitle_to_limit(title)

    #     return title

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
