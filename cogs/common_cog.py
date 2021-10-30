# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import json
import pathlib
import random
from datetime import datetime, timedelta

import aiofiles
import discord
import pytz
from discord.ext import commands, tasks

from cogs.utils.common import CommonUtil


class SatsukiCom(commands.Cog, name='皐月分類外コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.c = CommonUtil()

        root_path = pathlib.Path(__file__).parents[1]

        self.timer_json_path = root_path / 'data' / 'timer_dict.json'

        self.welcome_list = [286871252784775179, 609058923353341973]

        if not self.timer_json_path.exists():
            self.timer_dict = {}
            self.dump_json(self.timer_dict)

        with open(self.timer_json_path, encoding='utf-8') as f:
            self.timer_dict = json.load(f)

        self.multi_timer.stop()
        self.multi_timer.start()

    def dump_json(self, json_data: dict) -> None:
        """同期的にjsonを書き込む関数

        Args:
            json_data (dict): 辞書
        """
        with open(self.timer_json_path, "w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4,
                      separators=(',', ': '))

    async def aio_dump_json(self, json_data: dict) -> None:
        """非同期的にjsonを書き込む関数

        Args:
            json_data (dict): 辞書
        """
        async with aiofiles.open(self.timer_json_path, "w") as f:
            dict_string = json.dumps(json_data, ensure_ascii=False, indent=4,
                                     separators=(',', ': '))
            await f.write(dict_string)

    @commands.command(description="urlを貼るためのコマンド")
    async def url(self, ctx, call):
        """多分もう必要ない"""
        call = call.strip()
        if "http" in call:
            reply = f"外部サイトを貼らないでください.{ctx.author.mention}"
            msg = await ctx.reply(reply)
            await self.c.autodel_msg(msg)
            return
        elif "/" in call[0]:
            reply = f'{self.bot.root_url}{call[1:]}'
        else:
            reply = f"{self.bot.root_url}{call}"

        await ctx.reply(reply, mention_author=False)

    @commands.command(description="入力された数字の範囲内をランダムに返す関数")
    async def dice(self, ctx, num1: int, num2: int = 0):
        """`/dice {num1} {num2}`\nnum1~num2の間の数字を返します。num2は省略すると0になります。"""
        num_list = [num1, num2]
        num_list = sorted(num_list)

        if any(x >= 10000 for x in num_list):
            msg = await ctx.reply("入力値が大きすぎです")
            await self.c.autodel_msg(msg)

        elif any(x < 0 for x in num_list):
            msg = await ctx.reply("正の値を入力してください")
            await self.c.autodel_msg(msg)

        else:
            x = random.randint(num_list[0], num_list[1])
            await ctx.reply(f"出目は {x} です")

    @commands.command(aliases=['tm'], description="タイマーコマンド")
    # @commands.has_permissions(kick_members=True)
    async def timer(self, ctx, num: int = 30):
        """`/timer {num}`\n分刻みのタイマーです。精度はそこまで高くないです。"""
        if num >= 180:
            await ctx.reply(f'{ctx.author.mention}\n{num}分のタイマは設定できません\n最大時間は180分です')
            return

        dt_now = datetime.utcnow()
        dt_now = self.c.convert_utc_into_jst(dt_now)

        before_five = dt_now + timedelta(minutes=num - 5)
        just_now = dt_now + timedelta(minutes=num)

        if num <= 5:
            flag = 1
        else:
            flag = 0

        before_five = (dt_now + timedelta(minutes=num - 5)
                       ).strftime('%Y-%m-%d %H:%M:%S')
        just_now = (dt_now + timedelta(minutes=num)
                    ).strftime('%Y-%m-%d %H:%M:%S')
        dt_now = dt_now.strftime('%Y-%m-%d %H:%M:%S')

        self.timer_dict[dt_now] = {
            "-5": f"{before_five}",
            "just": f"{just_now}",
            "author": ctx.author.mention,
            "channel": ctx.channel.id,
            "flag": flag}

        await self.aio_dump_json(self.timer_dict)

        await ctx.reply(f"{ctx.author.mention} : {num}分のタイマーを開始します", mention_author=False)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.pending is True and after.pending is False:
            if any([after.guild.id == i for i in self.welcome_list]):
                channel = after.guild.system_channel
                await asyncio.sleep(3)
                embed = discord.Embed(
                    title=f"{after.guild.name}へようこそ",
                    colour=0x0080ff)
                embed.add_field(
                    name=f"こんにちは,{after.name}.",
                    value="<#548544598826287116>の確認ののち,<#464055645935501312>でアイサツをお願いします.",
                    inline=True)
                embed.add_field(
                    name=f"welcome {after.name}.",
                    value="please check and read <#569530661350932481> and then give a reaction to this msg.",
                    inline=True)
                embed.set_footer(text='読了したら何らかのリアクションをつけてください')
                try:
                    await channel.send(after.mention, embed=embed)
                except BaseException:
                    pass

    @tasks.loop(minutes=1.0)
    async def multi_timer(self):
        now = pytz.utc.localize(datetime.utcnow())

        now = self.c.convert_utc_into_jst(now)

        del_list = []

        for key in self.timer_dict.keys():
            dict_time_just = datetime.strptime(
                self.timer_dict[key]['just'], '%Y-%m-%d %H:%M:%S')
            dict_time_just = self.c.convert_native_jst_into_aware_jst(
                dict_time_just)

            dict_time_m5 = datetime.strptime(
                self.timer_dict[key]['-5'], '%Y-%m-%d %H:%M:%S')
            dict_time_m5 = self.c.convert_native_jst_into_aware_jst(
                dict_time_m5)

            if (days := (now - dict_time_just).days) > 1:
                del_list.append(key)

            elif days < - 30:
                del_list.append(key)

            elif dict_time_just < now:
                mention = self.timer_dict[key]['author']
                channel = self.bot.get_channel(self.timer_dict[key]['channel'])
                await channel.send(f'時間です : {mention}')

                del_list.append(key)

                await self.aio_dump_json(self.timer_dict)

            elif dict_time_m5 < now and self.timer_dict[key]['flag'] == 0:
                mention = self.timer_dict[key]['author']
                channel = self.bot.get_channel(self.timer_dict[key]['channel'])
                self.timer_dict[key]['flag'] = 1
                await channel.send(f'残り5分です : {mention}')

                await self.aio_dump_json(self.timer_dict)

        if len(del_list) > 0:
            for key in del_list:
                del self.timer_dict[key]
            await self.aio_dump_json(self.timer_dict)

    @multi_timer.before_loop
    async def before_timer(self):
        print('common waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(SatsukiCom(bot))
