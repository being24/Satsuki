import logging
import pathlib
import time
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

from .utils.common import CommonUtil

logger = logging.getLogger("discord")


class Admin(commands.Cog, name="管理用コマンド群"):
    """
    管理用のコマンドです
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.c = CommonUtil()

        self.master_path = pathlib.Path(__file__).parents[1]
        self.local_timezone = ZoneInfo("Asia/Tokyo")

        # 自動バックアップ用チャンネルID
        self.backup_channel_id = 745128369170939965

        self.auto_backup.stop()
        self.auto_backup.start()

    async def cog_check(self, ctx) -> bool:
        """管理者のみがコマンドを実行できるようにするチェック"""
        return ctx.guild is not None and await self.bot.is_owner(ctx.author)

    def get_data_files(self) -> List[pathlib.Path]:
        """データベースファイルのリストを取得する"""
        return list(self.master_path.glob("data/*.sqlite3"))

    def get_log_file_path(self) -> pathlib.Path:
        """ログファイルのパスを取得する"""
        return self.master_path / "log" / "discord.log"

    async def send_backup_files(self, destination) -> None:
        """バックアップファイルを指定された宛先に送信する

        Args:
            destination: 送信先（ctx または channel）
        """
        try:
            # データベースファイルを送信
            data_files = self.get_data_files()
            if data_files:
                discord_files = [discord.File(file) for file in data_files]
                await destination.send(files=discord_files)

            # ログファイルを送信
            log_file_path = self.get_log_file_path()
            if log_file_path.exists():
                discord_log = discord.File(log_file_path)
                await destination.send(files=[discord_log])
        except Exception as e:
            logger.error(f"Failed to send backup files: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """on_guild_join時に発火する関数"""
        if self.bot.user is None:
            return

        embed = discord.Embed(
            title="サーバーに参加しました",
            description=f"SCP公式チャット用utility-bot {self.bot.user.display_name}",
            color=0x2FE48D,
        )

        icon_url = None
        if self.bot.user.avatar:
            icon_url = self.bot.user.avatar.replace(format="png").url

        embed.set_author(name=self.bot.user.name, icon_url=icon_url)

        try:
            if guild.system_channel:
                await guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.command(aliases=["re"], hidden=True)
    async def reload(self, ctx: commands.Context):
        """全てのコグをリロードするコマンド"""
        reloaded_list = []
        for cog in self.master_path.glob("cogs/*.py"):
            try:
                await self.bot.unload_extension(f"cogs.{cog.stem}")
                await self.bot.load_extension(f"cogs.{cog.stem}")
                reloaded_list.append(cog.stem)
            except Exception as e:
                print(e)
                await ctx.reply(str(e), mention_author=False)
                return

        await ctx.reply(
            f"{' '.join(reloaded_list)}をreloadしました", mention_author=False
        )

    @commands.command(aliases=["st"], hidden=True)
    async def status(self, ctx: commands.Context, *, word: str = "Thread管理中"):
        """ボットのステータスを変更するコマンド"""
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.reply(f"ステータスを{word}に変更しました", mention_author=False)
        except (discord.Forbidden, discord.HTTPException) as e:
            logger.warning(f"ステータス変更に失敗しました: {e}")
            await ctx.reply("ステータス変更に失敗しました", mention_author=False)

    @commands.command(aliases=["p"], hidden=False, description="疎通確認")
    async def ping(self, ctx: commands.Context):
        """Pingによる疎通確認を行うコマンド"""
        start_time = time.time()
        mes = await ctx.reply("Pinging....")
        elapsed_time = round((time.time() - start_time) * 1000, 3)
        await mes.edit(content=f"pong!\n{elapsed_time}ms")

    @commands.command(aliases=["wh"], hidden=True)
    async def where(self, ctx: commands.Context):
        """現在参加しているサーバー一覧を表示するコマンド"""
        server_list = [guild.name.replace("\u3000", " ") for guild in self.bot.guilds]
        server_names = (
            "\n".join(server_list)
            if server_list
            else "参加しているサーバーがありません"
        )
        await ctx.reply(
            f"現在入っているサーバーは以下の通りです\n{server_names}",
            mention_author=False,
        )

    @commands.command(hidden=True)
    async def back_up(self, ctx: commands.Context):
        """手動バックアップコマンド"""
        await self.send_backup_files(ctx)

    @commands.command(hidden=True)
    async def restore_one(self, ctx: commands.Context):
        """ファイルを復元するコマンド"""
        if not ctx.message.attachments:
            await ctx.send("ファイルが添付されていません")
            return

        for attachment in ctx.message.attachments:
            try:
                await attachment.save(self.master_path / "data" / attachment.filename)
                await ctx.send(f"{attachment.filename}を追加しました")
            except Exception as e:
                await ctx.send(f"{attachment.filename}の保存に失敗しました: {e}")

    @commands.Cog.listener()
    async def on_message(self, _):
        """メッセージ受信時に発火する関数"""
        if not self.auto_backup.is_running():
            logger.warning("Auto backup task is not running, restarting...")
            self.auto_backup.start()

    @tasks.loop(minutes=1.0)
    async def auto_backup(self):
        """自動バックアップタスク"""
        now = datetime.now(self.local_timezone)

        if now.strftime("%H:%M") == "04:00":
            try:
                channel = self.bot.get_channel(self.backup_channel_id)
                if channel and hasattr(channel, "send"):
                    await self.send_backup_files(channel)
                else:
                    logger.error(
                        f"Backup channel {self.backup_channel_id} not found or invalid"
                    )
            except Exception as e:
                logger.error(f"Auto backup failed: {e}")

    @auto_backup.before_loop
    async def before_printer(self):
        print("admin waiting...")
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Admin(bot))
