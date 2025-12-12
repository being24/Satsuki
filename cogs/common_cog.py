import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands, tasks

logger = logging.getLogger("discord")

# 定数
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class SatsukiCom(commands.Cog, name="皐月分類外コマンド"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

        root_path: Path = Path(__file__).parents[1]

        self.timer_json_path: Path = root_path / "data" / "timer_dict.json"

        self.welcome_list: list[int] = [286871252784775179, 609058923353341973]

        self.jst_timezone: ZoneInfo = ZoneInfo("Asia/Tokyo")

        self.timer_dict: dict[str, dict[str, str | int]] = {}

        if not self.timer_json_path.exists():
            self.timer_dict = {}
            with self.timer_json_path.open("w", encoding="utf-8") as f:
                json.dump(self.timer_dict, f, ensure_ascii=False, indent=4)

        with self.timer_json_path.open("r", encoding="utf-8") as f:
            self.timer_dict = json.load(f)

    async def setup_hook(self) -> None:
        # self.bot.tree.copy_global_to(guild=MY_GUILD)
        pass

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """on_ready時に発火する関数"""
        self.multi_timer.stop()
        self.multi_timer.start()

        await self.bot.tree.sync()

    def _format_datetime(self, dt: datetime) -> str:
        """datetimeを文字列にフォーマットする

        Args:
            dt: フォーマットするdatetime

        Returns:
            フォーマットされた文字列
        """
        return dt.strftime(DATETIME_FORMAT)

    def _parse_datetime(self, dt_str: str) -> datetime:
        """文字列をdatetimeにパースする

        Args:
            dt_str: パースする文字列

        Returns:
            パースされたdatetime(JST)
        """
        return datetime.strptime(dt_str, DATETIME_FORMAT).replace(
            tzinfo=self.jst_timezone
        )

    async def _save_timer_dict(self) -> None:
        """タイマー辞書をJSONファイルに保存する"""
        async with aiofiles.open(self.timer_json_path, "w") as f:
            dict_string = json.dumps(
                self.timer_dict, ensure_ascii=False, indent=4, separators=(",", ": ")
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
    ) -> None:
        """入力された数字の範囲内をランダムに返す関数

        Args:
            num1 (int): 入力値1
            num2 (int, optional): 入力値2. Defaults to 0.
        """
        sorted_numbers: list[int] = sorted([num1, num2])
        min_value: int = sorted_numbers[0]
        max_value: int = sorted_numbers[1]

        result: int = random.randint(min_value, max_value)
        await interaction.response.send_message(
            f"INPUT: {max_value}~{min_value} OUTPUT: {result}"
        )

    @app_commands.command(name="timer", description="n分タイマー")
    async def timer(
        self,
        interaction: discord.Interaction,
        minutes: app_commands.Range[int, 1, 180] = 30,
    ) -> None:
        """n分タイマー

        Args:
            minutes (int, optional): 分数. Defaults to 30.
        """
        current_time: datetime = datetime.now(self.jst_timezone)

        # 5分以下の場合は事前通知済みとしてマーク
        is_notified: int = 1 if minutes <= 5 else 0

        pre_alarm_time_str: str = self._format_datetime(
            current_time + timedelta(minutes=minutes - 5)
        )
        alarm_time_str: str = self._format_datetime(
            current_time + timedelta(minutes=minutes)
        )
        current_time_str: str = self._format_datetime(current_time)

        channel_id: int = 0 if interaction.channel is None else interaction.channel.id

        self.timer_dict[current_time_str] = {
            "-5": pre_alarm_time_str,
            "just": alarm_time_str,
            "author": interaction.user.mention,
            "channel": channel_id,
            "flag": is_notified,
        }

        await self._save_timer_dict()

        await interaction.response.send_message(
            f"{interaction.user.mention} : {minutes}分のタイマーを開始します"
        )

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if before.pending is True and after.pending is False:
            if after.guild.id in self.welcome_list:
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
                except Exception as e:
                    logger.error(f"Failed to send welcome message: {e}")

    @commands.Cog.listener()
    async def on_message(self, _: discord.Message) -> None:
        if not self.multi_timer.is_running():
            logger.warning("multi_timer is not running, restarting...")
            self.multi_timer.start()

    @tasks.loop(minutes=1.0)
    async def multi_timer(self) -> None:
        current_time: datetime = datetime.now(self.jst_timezone)

        timers_to_delete: list[str] = []
        has_changes: bool = False

        for timer_key in list(self.timer_dict.keys()):
            timer_data: dict[str, str | int] = self.timer_dict[timer_key]

            alarm_time: datetime = self._parse_datetime(str(timer_data["just"]))
            pre_alarm_time: datetime = self._parse_datetime(str(timer_data["-5"]))

            try:
                channel = self.bot.get_channel(int(timer_data["channel"]))
            except Exception as e:
                logger.warning(
                    f"Failed to get channel for timer: {timer_key}, error: {e}"
                )
                continue

            if not isinstance(channel, discord.abc.Messageable):
                logger.warning(
                    f"Channel {timer_data['channel']} is not messageable for timer: {timer_key}"
                )
                continue  # 他のタイマーも処理する

            days_difference: int = (current_time - alarm_time).days

            # 期限切れまたは未来すぎるタイマーを削除
            if days_difference > 1 or days_difference < -30:
                timers_to_delete.append(timer_key)
                has_changes = True
                continue

            if alarm_time < current_time:
                user_mention: str = str(timer_data["author"])
                try:
                    await channel.send(f"時間です : {user_mention}")
                except Exception as e:
                    logger.warning(
                        f"Failed to send alarm message for timer: {timer_key}, error: {e}"
                    )
                timers_to_delete.append(timer_key)
                has_changes = True
                continue

            if pre_alarm_time < current_time and timer_data["flag"] == 0:
                user_mention: str = str(timer_data["author"])
                self.timer_dict[timer_key]["flag"] = 1
                try:
                    await channel.send(f"残り5分です : {user_mention}")
                except Exception as e:
                    logger.warning(
                        f"Failed to send 5min warning for timer: {timer_key}, error: {e}"
                    )
                has_changes = True

        if timers_to_delete:
            for timer_key in timers_to_delete:
                del self.timer_dict[timer_key]

        if has_changes:
            await self._save_timer_dict()

    @multi_timer.before_loop
    async def before_timer(self) -> None:
        print("common waiting...")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SatsukiCom(bot))
