import logging
import pathlib
import time
from datetime import datetime

import discord
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

logger = logging.getLogger("discord")


class Admin(commands.Cog, name="管理用コマンド群"):
    """
    管理用のコマンドです
    """

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

        self.master_path = pathlib.Path(__file__).parents[1]

        self.jst_timezone = ZoneInfo("Asia/Tokyo")

    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """on_guild_join時に発火する関数"""
        embed = discord.Embed(
            title="サーバーに参加しました",
            description=f"SCP公式チャット用utility-bot {self.bot.user.display_name}",
            color=0x2FE48D,
        )
        embed.set_author(
            name=f"{self.bot.user.name}", icon_url=f"{self.bot.user.avatar.url}"
        )
        try:
            await guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        """on_ready時に発火する関数"""
        self.auto_backup.stop()
        self.auto_backup.start()

    @commands.command(aliases=["re"], hidden=True)
    async def reload(self, ctx):
        reloaded_list = []
        for cog in self.master_path.glob("cogs/*.py"):
            try:
                await self.bot.unload_extension(f"cogs.{cog.stem}")
                await self.bot.load_extension(f"cogs.{cog.stem}")
                reloaded_list.append(cog.stem)
            except Exception as e:
                print(e)
                await ctx.reply(e, mention_author=False)

        await ctx.reply(
            f"{' '.join(reloaded_list)}をreloadしました", mention_author=False
        )

    @commands.command(aliases=["st"], hidden=True)
    async def status(self, ctx, word: str = "info bot Satsuki"):
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.reply(f"ステータスを{word}に変更しました", mention_author=False)

        except discord.Forbidden or discord.HTTPException:
            logger.error("status change error")

    @commands.command(aliases=["p"], hidden=False, description="疎通確認")
    async def ping(self, ctx):
        """Pingによる疎通確認を行うコマンド"""
        start_time = time.time()
        mes = await ctx.reply("Pinging....")
        await mes.edit(
            content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms"
        )

    # TODO : fix this command
    @commands.command(aliases=["wh"], hidden=True)
    async def where(self, ctx):
        server_list = [i.name.replace("\u3000", " ") for i in ctx.bot.guilds]

        # 10こずつに分割
        server_list = [server_list[i : i + 10] for i in range(0, len(server_list), 10)]

        await ctx.reply(
            "現在入っているサーバーは以下の通りです",
            mention_author=False,
        )
        for server in server_list:
            await ctx.send("\n".join(server))

    @commands.command(hidden=True)
    async def back_up(self, ctx):
        # sql_files = [filename for filename in os.listdir(self.master_path  "/data") if filename.endswith(".sqlite3")]
        data_files = list(self.master_path.glob("data/*.sqlite3"))

        discord_files = [discord.File(file) for file in data_files]

        await ctx.send(files=discord_files)

        log_file = self.master_path / "log" / "discord.log"
        discord_log = discord.File(log_file)

        await ctx.send(files=[discord_log])

    @commands.command(hidden=True)
    async def restore_one(self, ctx: commands.Context):
        if ctx.message.attachments is None:
            await ctx.send("ファイルが添付されていません")

        for attachment in ctx.message.attachments:
            await attachment.save(self.master_path / "data" / attachment.filename)
            await ctx.send(f"{attachment.filename}を追加しました")

    @commands.Cog.listener()
    async def on_message(self, _: discord.Message):
        if not self.auto_backup.is_running():
            logger.warning("auto_backup is not running, restarting...")
            self.auto_backup.start()

    @tasks.loop(minutes=1.0)
    async def auto_backup(self):
        now = datetime.now(self.jst_timezone)
        now_hm = now.strftime("%H:%M")

        if now_hm == "04:00":
            channel = self.bot.get_channel(745128369170939965)

            data_files = list(self.master_path.glob("data/*.sqlite3"))

            discord_files = [discord.File(file) for file in data_files]

            await channel.send(files=discord_files)

            log_file = self.master_path / "log" / "discord.log"
            discord_log = discord.File(log_file)

            await channel.send(files=[discord_log])

    @auto_backup.before_loop
    async def before_printer(self):
        print("admin waiting...")
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Admin(bot))
