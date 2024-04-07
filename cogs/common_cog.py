import asyncio
import json
import logging
import pathlib
import random
from datetime import datetime, timedelta

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

logger = logging.getLogger("discord")


class SatsukiCom(commands.Cog, name="皐月分類外コマンド"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        root_path = pathlib.Path(__file__).parents[1]

        self.timer_json_path = root_path / "data" / "timer_dict.json"

        self.welcome_list = [286871252784775179, 609058923353341973]

        self.jst_timezone = ZoneInfo("Asia/Tokyo")

        if not self.timer_json_path.exists():
            self.timer_dict = {}
            with open(self.timer_json_path, "w") as f:
                json.dump(self.timer_dict, f, ensure_ascii=False, indent=4)

        with open(self.timer_json_path, encoding="utf-8") as f:
            self.timer_dict = json.load(f)

    async def setup_hook(self):
        # self.bot.tree.copy_global_to(guild=MY_GUILD)
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        """on_ready時に発火する関数"""
        self.multi_timer.stop()
        self.multi_timer.start()

        await self.bot.tree.sync()

    async def aio_dump_json(self, json_data: dict) -> None:
        """非同期的にjsonを書き込む関数

        Args:
            json_data (dict): 辞書
        """
        async with aiofiles.open(self.timer_json_path, "w") as f:
            dict_string = json.dumps(
                json_data, ensure_ascii=False, indent=4, separators=(",", ": ")
            )
            await f.write(dict_string)

    @app_commands.command(
        name="dice", description="入力された数字の範囲内をランダムに返す関数"
    )
    async def dice(
        self,
        interaction: discord.Interaction,
        num1: app_commands.Range[int, 1, 10000],
        num2: app_commands.Range[int, 1, 10000] = 0,
    ):
        """入力された数字の範囲内をランダムに返す関数

        Args:
            num1 (int): 入力値1
            num2 (int, optional): 入力値2. Defaults to 0.
        """

        # sort the numbers
        num_list = [num1, num2]
        num_list = sorted(num_list)

        x = random.randint(num_list[0], num_list[1])
        await interaction.response.send_message(
            f"INPUT: {num_list[1]}~{num_list[0]} OUTPUT: {x}"
        )

    @app_commands.command(name="timer", description="n分タイマー")
    async def timer(
        self,
        interaction: discord.Interaction,
        minutes: app_commands.Range[int, 1, 180] = 30,
    ):
        """n分タイマー

        Args:
            num (int, optional): 分数. Defaults to 30.
        """
        dt_now = datetime.now(self.jst_timezone)

        before_five = dt_now + timedelta(minutes=minutes - 5)
        just_now = dt_now + timedelta(minutes=minutes)

        if minutes <= 5:
            flag = 1
        else:
            flag = 0

        before_five = (dt_now + timedelta(minutes=minutes - 5)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        just_now = (dt_now + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        dt_now = dt_now.strftime("%Y-%m-%d %H:%M:%S")

        if interaction.channel is None:
            channel_id = 0
        else:
            channel_id = interaction.channel.id

        self.timer_dict[dt_now] = {
            "-5": f"{before_five}",
            "just": f"{just_now}",
            "author": interaction.user.mention,
            "channel": channel_id,
            "flag": flag,
        }

        await self.aio_dump_json(self.timer_dict)

        await interaction.response.send_message(
            f"{interaction.user.mention} : {minutes}分のタイマーを開始します"
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.pending is True and after.pending is False:
            if any([after.guild.id == i for i in self.welcome_list]):
                channel = after.guild.system_channel

                if not isinstance(channel, discord.abc.Messageable):
                    return

                await asyncio.sleep(3)
                embed = discord.Embed(
                    title=f"{after.guild.name}へようこそ", colour=0x0080FF
                )
                embed.add_field(
                    name=f"こんにちは,{after.name}.",
                    value="<#548544598826287116>の確認ののち,<#464055645935501312>でアイサツをお願いします.",
                    inline=True,
                )
                embed.add_field(
                    name=f"welcome {after.name}.",
                    value="please check and read <#569530661350932481> and then give a reaction to this msg.",
                    inline=True,
                )
                embed.set_footer(text="読了したら何らかのリアクションをつけてください")
                try:
                    await channel.send(after.mention, embed=embed)
                except BaseException:
                    pass

    @commands.Cog.listener()
    async def on_message(self, _: discord.Message):
        if not self.multi_timer.is_running():
            logger.warning("auto_backup is not running, restarting...")
            self.multi_timer.start()

    @tasks.loop(minutes=1.0)
    async def multi_timer(self):
        now = datetime.now(self.jst_timezone)

        del_list = []

        for key in self.timer_dict.keys():
            alarm_time = datetime.strptime(
                self.timer_dict[key]["just"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=self.jst_timezone)

            pre_alarm_time = datetime.strptime(
                self.timer_dict[key]["-5"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=self.jst_timezone)

            channel = self.bot.get_channel(self.timer_dict[key]["channel"])

            if not isinstance(channel, discord.abc.Messageable):
                return

            if (days := (now - alarm_time).days) > 1:
                del_list.append(key)

            elif days < -30:
                del_list.append(key)

            elif alarm_time < now:
                mention = self.timer_dict[key]["author"]
                await channel.send(f"時間です : {mention}")

                del_list.append(key)
                await self.aio_dump_json(self.timer_dict)

            elif pre_alarm_time < now and self.timer_dict[key]["flag"] == 0:
                mention = self.timer_dict[key]["author"]
                self.timer_dict[key]["flag"] = 1
                await channel.send(f"残り5分です : {mention}")

                await self.aio_dump_json(self.timer_dict)

        if len(del_list) > 0:
            for key in del_list:
                del self.timer_dict[key]
            await self.aio_dump_json(self.timer_dict)

    @multi_timer.before_loop
    async def before_timer(self):
        print("common waiting...")
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(SatsukiCom(bot))
