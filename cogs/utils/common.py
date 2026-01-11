import datetime
import logging
from zoneinfo import ZoneInfo

import discord
from discord.ext.commands import bot
from pydantic import BaseModel

from .page_models import PageListItem

logger = logging.getLogger("discord")


class SearchResult(BaseModel):
    """表示用に正規化した検索結果データ."""

    fullname: str
    title: str
    created_at: datetime.datetime
    created_by_unix: str
    rating: int
    tags: list[str]
    metatitle: str | None
    page_id: int


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

    def create_detail_embed(self, data: SearchResult) -> discord.Embed:
        """詳細をembedにする関数、tzとか文字数制限とかはよしなにしてくれる

        Args:
            data (SearchResult): 記事データ

        Returns:
            discord.Embed: 色々調整したデータ
        """
        tags = (" ").join(data.tags)

        title = self.select_title(data)
        title = self.reap_metatitle_to_limit(title)

        embed = discord.Embed(
            title=f"{title}", url=f"{self.root_url}{data.fullname}", color=0x8F1919
        )
        embed.add_field(
            name="created_by", value=f"{data.created_by_unix}", inline=False
        )
        embed.add_field(
            name="投稿日",
            value=f"created at <t:{int(data.created_at.timestamp())}:D>",
            inline=False,
        )
        embed.add_field(name="rate", value=f"{data.rating}", inline=True)
        embed.add_field(name="tags", value=f"{tags}", inline=True)
        embed.add_field(
            name="rate trends",
            value=f"[link](https://ayame.scp-jp.net/chart.html?id={data.page_id})",
            inline=True,
        )
        embed.add_field(
            name="data link",
            value=f"[link](https://data.scp-jp.com/pages/{data.page_id})",
            inline=True,
        )

        embed.set_footer(text=f"page_id: {data.page_id}")

        return embed

    def select_title(self, data: SearchResult) -> str:
        """メタタイトルをがあればそちらを、そうでなければtitleを返す関数

        Args:
            data (SearchResult)

        Returns:
            str
        """
        if data.metatitle not in ("", None):
            title = data.metatitle
        elif data.title not in ("", None):
            title = data.title
        else:
            title = data.fullname

        title = self.reap_metatitle_to_limit(title)

        return title

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

    @staticmethod
    def from_page_item(item: PageListItem) -> SearchResult:
        """PageListItemを表示用SearchResultへ正規化する"""

        return SearchResult(
            fullname=item.fullname,
            title=item.title,
            created_at=datetime.datetime.fromtimestamp(item.createdAt),
            created_by_unix=item.createdByName or "unknown",
            rating=item.rating,
            tags=item.tags or [],
            metatitle=item.fullname,
            page_id=item.wikidotId,
        )
