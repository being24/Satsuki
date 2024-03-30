import logging
from datetime import datetime, timedelta
from typing import List, Optional

import aiohttp
import discord
import feedparser
import html2text
from discord import app_commands

# from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ui import Modal, TextInput

# from more_itertools import divide
from pydantic.dataclasses import dataclass
from zoneinfo import ZoneInfo

# from cogs.utils.common import CommonUtil
from cogs.utils.criticism_manager import CriticismManager, ReserveData

logger = logging.getLogger("discord")
jst_timezone = ZoneInfo("Asia/Tokyo")
utc_timezone = ZoneInfo("UTC")


@dataclass
class RssData:
    title: str
    link: str
    published_time: datetime
    author: str
    content: str


class ReserveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.criticism_manager = CriticismManager()

    @discord.ui.button(
        label="予約",
        style=discord.ButtonStyle.success,
        custom_id="persistent_view:reserve",
    )
    async def ok(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        # await interaction.response.send_message(f"{interaction.user.mention} OK!")
        class ProxyModal(Modal, title="予約フォーム"):
            criticism_mng = CriticismManager()

            article_title = TextInput(
                label="タイトル",
                placeholder="タイトルを入力してください",
                style=discord.TextStyle.short,
            )
            url = TextInput(
                label="URL",
                placeholder="URLを入力してください",
                style=discord.TextStyle.short,
            )

            async def on_submit(self, interaction: discord.Interaction):
                # get datetime from interaction
                reserve_datetime = interaction.created_at

                data = ReserveData(
                    reserve_id=0,
                    title=self.article_title.value,
                    link=self.url.value,
                    author_id=interaction.user.id,
                    reserve_time=reserve_datetime,
                )

                # dbに登録
                await self.criticism_mng.add_reserve_data(data)

                await interaction.response.send_message(
                    "予約完了しました", ephemeral=True
                )

            async def on_error(
                self, interaction: discord.Interaction, error: Exception
            ) -> None:
                logger.error(f"Error: {error}")

        await interaction.response.send_modal(ProxyModal())

    @discord.ui.button(
        label="一覧",
        style=discord.ButtonStyle.primary,
        custom_id="persistent_view:list",
    )
    async def reserve_list(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # 今の時間を取得
        jst_now = datetime.now(jst_timezone)

        # 3時間前に変換
        start = jst_now - timedelta(hours=3)

        # 3時間後に変換
        end = jst_now + timedelta(hours=3)

        # startとendの間の20時45分を取得
        limen = start.replace(hour=20, minute=45, second=0)

        # utcに変換
        start = start.astimezone(utc_timezone)
        end = end.astimezone(utc_timezone)
        limen = limen.astimezone(utc_timezone)

        # 今日の予約分を取得
        reserve_list = await self.criticism_manager.get_reserve_data_from_date_and_id(
            user_id=interaction.user.id, start=start, end=end
        )

        # reserve_listをreserve_timeでソート
        reserve_list.sort(key=lambda x: x.reserve_time)

        if len(reserve_list) == 0:
            await interaction.response.send_message(
                "本日の予約はありません", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="予約一覧",
            description="あなたの本日の予約は以下のとおりです",
            color=0x0000A0,
        )

        for reserve in reserve_list:
            reserve_time_stamp = f"<t:{int(reserve.reserve_time.timestamp())}:f>"
            author = interaction.guild.get_member(reserve.author_id)

            if author is None:
                author = "Unknown"

            # 8時45分以前の予約は、authorのあとに(受付時間外)をつける
            if reserve.reserve_time < limen:
                author = f"{author} (受付時間外)"

            embed.add_field(
                name=f"{author}",
                value=f"{reserve.reserve_id} : [{reserve.title}]({reserve.link})\tat: {reserve_time_stamp}",
                inline=False,
            )

        embed.set_footer(text="受付時間外の予約は無効です!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # @discord.ui.button(
    #     label="キャンセル",
    #     style=discord.ButtonStyle.danger,
    #     custom_id="persistent_view:cancel",
    # )
    # async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.send_message(f"{interaction.user.mention} Canceled!")


class CritiqueCog(commands.Cog, name="批評定例会用コマンド"):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.SCP_JP = "http://scp-jp.wikidot.com"

        self.rss_addr = "http://scp-jp.wikidot.com/feed/forum/t-13064618.xml"

        self.criticism_mng = CriticismManager()

    async def setup_hook(self):
        # self.bot.tree.copy_global_to(guild=MY_GUILD)
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        await self.criticism_mng.create_table()

        await self.bot.tree.sync()

    @app_commands.command(name="agenda", description="定例会告知用コマンド")
    @app_commands.checks.has_permissions(kick_members=True)
    async def agenda(
        self,
        interaction: discord.Interaction,
    ):
        """定例会告知スレッドRSSから書き込みを取得、送信するコマンド"""
        await interaction.response.defer()

        content_list = await self.get_content_from_rss(self.rss_addr)
        data = content_list[0]

        embed = discord.Embed(
            title="本日の定例会テーマのお知らせです", url=data.link, color=0x0000A0
        )

        if len(data.content) > 1000:
            content = f"{data.content[:1000]}..."
        else:
            content = data.content

        embed.add_field(name=data.title, value=content, inline=False)

        embed.add_field(
            name="Post Link",
            value=f"[link]({data.link})",
            inline=False,
        )

        embed.add_field(
            name="投稿時間",
            value=f"published at <t:{int(data.published_time.timestamp())}:f>",
            inline=False,
        )

        embed.set_footer(text=f"published by {data.author}")

        await interaction.followup.send(embed=embed)

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
            content = html2text.html2text(entry["content"][0]["value"])
            content = content.replace(")", ") ")
            content = content.replace("-\n", "-")

            published_time = self.from_struct_time_to_datetime(entry["published"])

            if published_time is None:
                published_time = datetime.fromtimestamp(0)

            data = RssData(
                title=entry["title"],
                link=entry["link"],
                published_time=published_time,
                author=entry["wikidot_authorname"],
                content=content,
            )
            scp_rss.append(data)

        return scp_rss

    def from_struct_time_to_datetime(self, struct_time: str) -> Optional[datetime]:
        """wikidot-RSSの文字列をdatetimeに変換する

        Args:
            struct_time (str): RSSの文字列

        Returns:
            Optional[datetime]: awareなdatetime
        """

        try:
            postdate = datetime.strptime(
                struct_time, "%a, %d %b %Y %H:%M:%S %z"
            ).replace(tzinfo=utc_timezone)

            return postdate
        except ValueError:
            return None

    @app_commands.command(
        name="reserve_button", description="予約用ボタンの設置コマンド"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def reserve_button(self, interaction: discord.Interaction):
        """予約用ボタンの設置コマンド"""
        view = ReserveView()
        await interaction.response.send_message(
            "定例会の予約には以下のボタンを使用してください", view=view
        )

    @app_commands.command(name="draft", description="本日の下書き予約を表示します")
    @app_commands.checks.has_permissions(kick_members=True)
    async def draft(self, interaction: discord.Interaction, index: int = 0):
        """本日の下書き予約を表示します.引数に数字を与えるとその下書き予約を表示します."""
        await interaction.response.defer()

        # 今の時間を取得
        jst_now = datetime.now(jst_timezone)

        # 3時間前に変換
        start = jst_now - timedelta(hours=3)

        # 3時間後に変換
        end = jst_now + timedelta(hours=3)

        # startとendの間の20時45分を取得
        limen = start.replace(hour=20, minute=45, second=0)

        # utcに変換
        start = start.astimezone(utc_timezone)
        end = end.astimezone(utc_timezone)
        limen = limen.astimezone(utc_timezone)

        # 今日の予約分を取得
        reserve_list = await self.criticism_mng.get_reserve_data_from_date(
            start=start, end=end
        )

        # reserve_listをreserve_timeでソート
        reserve_list.sort(key=lambda x: x.reserve_time)

        if len(reserve_list) == 0:
            await interaction.followup.send("本日の予約はありません")
            return

        if index == 0:
            embed = discord.Embed(
                title="本日の予約一覧",
                description=f"本日の予約は全{len(reserve_list)}件です",
                color=0xFF0080,
            )

            for reserve in reserve_list:
                reserve_time_stamp = f"<t:{int(reserve.reserve_time.timestamp())}:f>"
                author = interaction.guild.get_member(reserve.author_id)

                if author is None:
                    author = "Unknown"

                # 8時45分以前の予約は、authorのあとに(受付時間外)をつける
                if reserve.reserve_time < limen:
                    author = f"{author} (受付時間外)"

                embed.add_field(
                    name=author,
                    value=f"{reserve.reserve_id} : [{reserve.title}]({reserve.link})\tat: {reserve_time_stamp}",
                    inline=False,
                )

            embed.set_footer(text="受付時間外の予約は無効です!")
            await interaction.followup.send(embed=embed)
            return

        else:
            # indexがreserve_idと一致するものを取得
            reserve = next((x for x in reserve_list if x.reserve_id == index), None)

            if reserve is None:
                await interaction.followup.send("予約が見つかりませんでした")
                return

            embed = discord.Embed(
                title="次の批評予約",
                color=0xFF0080,
            )

            author = interaction.guild.get_member(reserve.author_id)

            if author is None:
                author = "Unknown"

            reserve_time_stamp = f"<t:{int(reserve.reserve_time.timestamp())}:f>"

            embed.add_field(
                name=author,
                value=f"{reserve.reserve_id} : [{reserve.title}]({reserve.link})\tat: {reserve_time_stamp}",
                inline=False,
            )

            embed.set_footer(text="受付時間外の予約は無効です!")

            await interaction.followup.send(embed=embed)

    # @commands.command(
    #     aliases=["sh"], description="リアクションをつけた人を均等に分割するコマンド"
    # )
    # @commands.has_permissions(kick_members=True)
    # async def shuffle(self, ctx, num: int = 2):
    #     """あんまり使ってるところを見たことはない"""
    #     settime = 10.0 * 60
    #     reaction_member = []
    #     emoji_in = "\N{THUMBS UP SIGN}"
    #     emoji_go = "\N{NEGATIVE SQUARED CROSS MARK}"

    #     embed = discord.Embed(
    #         title="下書き批評に参加するメンバーを募集します", colour=0x1E90FF
    #     )
    #     embed.add_field(
    #         name=f"参加する方はリアクション{emoji_in}を押してください",
    #         value="ご参加お待ちしております",
    #         inline=True,
    #     )
    #     embed.set_footer(text="少し待ってからリアクションをつけてください")

    #     msg = await ctx.reply(embed=embed)

    #     await msg.add_reaction(emoji_in)
    #     await msg.add_reaction(emoji_go)
    #     await asyncio.sleep(0.3)

    #     while True:
    #         try:
    #             reaction, user = await self.bot.wait_for(
    #                 "reaction_add", timeout=settime
    #             )
    #         except asyncio.TimeoutError:
    #             timeout = await ctx.reply("タイムアウトしました")
    #             await self.c.autodel_msg(msg=timeout)
    #             break
    #         else:
    #             if str(reaction.emoji) == emoji_go:
    #                 if ctx.author.id == user.id:
    #                     if len(reaction_member) < num:
    #                         await ctx.send("最低人数を満たしませんでした")
    #                         await msg.clear_reactions()
    #                         break

    #                     await ctx.send("募集を終了しました")

    #                     reaction_member = list(set(reaction_member))

    #                     random.shuffle(reaction_member)
    #                     divided_reaction_member = list(divide(num, reaction_member))

    #                     embed = discord.Embed(
    #                         title="割り振りは以下の通りです", color=0x1E90FF
    #                     )

    #                     for i in range(num):
    #                         str_member = "\n".join(divided_reaction_member[i])
    #                         embed.add_field(
    #                             name=f"group:{i}", value=f"{str_member}", inline=True
    #                         )
    #                     embed.set_footer(text="よろしくお願いします")

    #                     await msg.edit(embed=embed)
    #                     await msg.clear_reactions()

    #                     break
    #                 else:
    #                     await msg.remove_reaction(str(reaction.emoji), user)

    #             elif str(reaction) == emoji_in:
    #                 if user.id in reaction_member:
    #                     pass
    #                 else:
    #                     reaction_member.append(user.mention)


async def setup(bot):
    await bot.add_cog(CritiqueCog(bot))
    bot.add_view(ReserveView())
