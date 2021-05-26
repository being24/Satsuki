# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import json
import os
import random
from datetime import datetime, timedelta

import aiofiles
import discord
from discord.ext import commands, tasks

from cogs.utils.common import CommonUtil


class SatsukiCom(commands.Cog, name='皐月分類外コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.c = CommonUtil()

        self.SCP_JP = "http://scp-jp.wikidot.com"
        self.root_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        self.welcome_list = [286871252784775179, 609058923353341973]
        self.BRANCHS = [
            'jp',
            'en',
            'ru',
            'ko',
            'es',
            'cn',
            'cs',
            'fr',
            'pl',
            'th',
            'de',
            'it',
            'ua',
            'pt',
            'uo']  # 外部に依存させたいな

        self.json_name = self.root_path + "/data/timer_dict.json"

        if not os.path.isfile(self.json_name):
            self.timer_dict = {}
            self.dump_json(self.timer_dict)

        with open(self.json_name, encoding='utf-8') as f:
            self.timer_dict = json.load(f)

        self.multi_timer.stop()
        self.multi_timer.start()

    def dump_json(self, json_data: dict) -> None:
        """同期的にjsonを書き込む関数

        Args:
            json_data (dict): 辞書
        """
        with open(self.json_name, "w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4,
                      separators=(',', ': '))

    async def aio_dump_json(self, json_data: dict) -> None:
        """非同期的にjsonを書き込む関数

        Args:
            json_data (dict): 辞書
        """
        async with aiofiles.open(self.json_name, "w") as f:
            dict_string = json.dumps(json_data, ensure_ascii=False, indent=4,
                                     separators=(',', ': '))
            await f.write(dict_string)

    @commands.command()
    async def url(self, ctx, call):
        call = call.strip()
        if "http" in call:
            reply = f"外部サイトを貼らないでください.{ctx.author.mention}"
            msg = await ctx.reply(reply)
            await self.c.autodel_msg(msg)
            return
        elif "/" in call[0:1]:
            reply = self.SCP_JP + call
        else:
            reply = f"{self.SCP_JP}/{call}"

        await ctx.reply(reply, mention_author=False)

    @commands.command()
    async def dice(self, ctx, num1: int, num2: int = 0):
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

    '''
    @commands.command()
    async def rand(self, ctx, brt: typing.Optional[str] = 'all'):
        try:
            result = pd.read_csv(
                self.root_path +
                "/data/scps.csv",
                index_col=0)
        except FileNotFoundError as e:
            print(e)
            return

        brt = brt.lower()

        if brt in self.BRANCHS:
            result = result.query('branches in @brt')

        result = result.sample()

        result = result[0:1].values.tolist()
        result = itertools.chain(*result)
        result = list(result)

        await ctx.send(f"{result[1]}\n{self.SCP_JP}{result[0]}")
    '''

    @commands.command(aliases=['tm'])
    # @commands.has_permissions(kick_members=True)
    async def timer(self, ctx, num: int = 30):
        today = datetime.today()
        before_five = today + timedelta(minutes=num - 5)
        just_now = today + timedelta(minutes=num)

        for key in list(self.timer_dict.keys()):
            dict_time = datetime.strptime(
                self.timer_dict[key]['just'], '%Y-%m-%d %H:%M:%S')
            if today > dict_time - timedelta(minutes=5):
                self.timer_dict.pop(key, None)

        before_five = (today + timedelta(minutes=num - 5)
                       ).strftime('%Y-%m-%d %H:%M:%S')
        just_now = (today + timedelta(minutes=num)
                    ).strftime('%Y-%m-%d %H:%M:%S')
        today = today.strftime('%Y-%m-%d %H:%M:%S')

        self.timer_dict[today] = {
            "-5": f"{before_five}",
            "just": f"{just_now}",
            "author": ctx.author.mention,
            "channel": ctx.channel.id,
            "flag": 0}

        await self.aio_dump_json(self.timer_dict)

        await ctx.reply(f"{ctx.author.mention} : {num}分のタイマーを開始します", mention_author=False)

    @commands.command()
    async def help_old(self, ctx):
        msg = discord.Embed(
            title='本BOTの使い方を説明させていただきます.',
            description=f'よろしくお願いします.{ctx.author.mention}',
            colour=0xad1457)
        msg.add_field(
            name="/scp $scpnumber-branch$",
            value="SCP内の各国記事のURLとタイトルを返します(ex1 /scp 173 ex2 /scp 1970jp)",
            inline=False)
        msg.add_field(
            name="/search(src) $word$",
            value="ヒットした記事を表示します.",
            inline=False)
        msg.add_field(
            name="/tale $word$",
            value="taleのURL,タイトル,著者を返します(ex /tale shinjimao04)",
            inline=False)
        msg.add_field(name="/proposal(prop) $word$",
                      value="提言のURL,タイトルを返します(ex /proposal 艦橋)", inline=False)
        msg.add_field(name="/joke $word$",
                      value="jokeのURL,タイトルを返します(ex /joke ブライト)", inline=False)
        msg.add_field(
            name="/author(auth) $word$",
            value="ヒットした著者ページを表示します.",
            inline=False)
        msg.add_field(
            name="/explained(ex) $word$",
            value="ヒットしたex-scpを表示します.",
            inline=False)
        msg.add_field(
            name="/guide(gd) $word$",
            value="ヒットしたガイドページを表示します.",
            inline=False)
        msg.add_field(
            name="/draft(df)",
            value="本日の下書き予約を表示します.引数に数字を与えるとその下書き予約を表示します.",
            inline=False)
        msg.add_field(name="/url $url$",
                      value="$url$をSCPJPのアドレスに追加して返します.", inline=False)
        msg.add_field(name="/dice $int$ $int:default=0$",
                      value="サイコロを振って返します.", inline=False)
        msg.add_field(name="/last_updated(lu)",
                      value="データベースの最終更新日を表示します.", inline=False)
        msg.add_field(name="/rand",
                      value="ランダムに記事を表示します.引数で支部が指定できます.", inline=False)
        msg.add_field(name="/help", value="ヘルプです.", inline=False)
        msg.add_field(
            name="/timer $minutes:default=30$",
            value="簡易的なタイマーです.5分以上の場合、残り5分でもお知らせします.予期せぬ再起動にも安心！",
            inline=False)
        msg.add_field(
            name="/meeting(mt)",
            value="#scp-jp 定例会のお知らせスレッドから定例会のテーマを取得表示します.",
            inline=False)
        msg.add_field(
            name="/shuffle(sh) $num:default=2$",
            value="定例会の下書き批評回における振り分けを行います.",
            inline=False)
        msg.add_field(
            name="追記",
            value="バグ等を発見した場合は、然るべき場所にご報告ください.\n__**また、動作確認にはDMを使用することも可能です**__",
            inline=False)

        await ctx.reply(embed=msg)

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
    async def multi_timer(self):  # 要修正
        now = datetime.now()
        del_list = []

        for key in self.timer_dict.keys():
            dict_time_just = datetime.strptime(
                self.timer_dict[key]['just'], '%Y-%m-%d %H:%M:%S')
            dict_time_m5 = datetime.strptime(
                self.timer_dict[key]['-5'], '%Y-%m-%d %H:%M:%S')

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
