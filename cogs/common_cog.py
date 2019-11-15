# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import html
import itertools
import json
import os
import random
import subprocess
import sys
import typing
from datetime import datetime, timedelta

import aiohttp
import discord
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from pytz import timezone

import libs as lib


class Tachibana_Com(commands.Cog, name='一般コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://ja.scp-wiki.net"
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn', 'cs',
                        'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']

        with open(self.master_path + "/data/timer_dict.json", encoding='utf-8') as f:
            self.timer_dict = json.load(f)

        self.multi_timer.start()

    def cog_unload(self):
        self.multi_timer.cancel()

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command(aliases=['df'])
    @commands.has_permissions(kick_members=True)
    async def draft(self, ctx, num: typing.Optional[int] = 0):
        target_url = 'http://njr-sys.net/irc/draftReserve/'

        d_today = (datetime.now() + timedelta(hours=-3)).date()
        # d_today = '2019-10-12'
        response = requests.get(target_url + str(d_today))

        soup = BeautifulSoup(response.text, "html.parser")

        limen_object = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')

        url = []
        time = []
        title = []
        author = []

        for i, detail in enumerate(soup.find_all(class_='irc-table__message')):
            if i % 4 == 0:
                time_object = datetime.strptime(
                    f'{d_today}-{detail.string.replace(" ", "")}',
                    '%Y-%m-%d-%H:%M:%S')
                if time_object < limen_object:
                    flag = 0
                else:
                    flag = 1
                    time.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 1:
                author.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 2:
                title.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 3:
                url.append(detail.a.get("href"))
            else:
                pass

        if len(url) == 0:
            await ctx.send("本日の予約はありません")
            return

        title_message = "下書き批評予約システムからデータを取得します"

        if num == 0:
            embed = discord.Embed(
                title=title_message,
                description=f"本日の下書き批評予約は全{len(url)}件です",
                color=0xff0080)

            for i in range(len(author)):
                embed.add_field(
                    name=author[i],
                    value=f'{i+1} : [{title[i]}]({url[i]})\tat: {time[i]}',
                    inline=False)

            embed.set_footer(text=f"受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title=title_message,
                description=f"{num}/{len(url)}件目の下書きです",
                color=0xff0080)
            num = num - 1
            embed.add_field(
                name=author[num],
                value=f'{num+1} : [{title[num]}]({url[num]})\tat: {time[num]}',
                inline=False)

            embed.set_footer(text=f"受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

    @draft.error
    async def unknown_error_handler(self, ctx, error):
        if discord.ext.commands.errors.MissingPermissions:
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command()
    async def url(self, ctx, call):
        call = call.replace(" ", "").replace("　", "")
        if "http" in call:
            reply = "外部サイトを貼らないでください." + ctx.author.mention
        elif "/" in call[0:1]:
            reply = self.SCP_JP + call
        else:
            reply = self.SCP_JP + "/" + call

        if reply is not None:
            await ctx.send(reply)

    @url.error
    async def url_error(self, ctx, error):
        if discord.ext.commands.errors.BadArgument:
            await ctx.send('入力値が不正です')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command()
    async def dice(self, ctx, num1: int, num2: typing.Optional[int] = 0):
        nums = sorted([num1, num2])

        if any(x >= 10000 for x in nums):
            await ctx.send("入力値が大きすぎです")
        elif any(x < 10000 for x in nums):
            await ctx.send("正の値を入力してください")

        else:
            x = random.randint(nums[0], nums[1])
            if x is not None:
                await ctx.send("出目は " + str(x) + " です")

    @dice.error
    async def dice_error(self, ctx, error):
        if discord.ext.commands.errors.BadArgument:
            await ctx.send('入力値が不正です')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['lu'])
    async def last_updated(self, ctx):
        last_update_utime = os.path.getmtime(
            self.master_path + "/data/scps.csv")
        last_update_UTC_nv = datetime.fromtimestamp(int(last_update_utime))
        last_update_JST = timezone('Asia/Tokyo').localize(last_update_UTC_nv)
        await ctx.send(f"データベースの最終更新日時は{last_update_JST}です")

    @last_updated.error
    async def unknown_error_handler(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command()
    async def rand(self, ctx, brt: typing.Optional[str] = 'all'):
        try:
            result = pd.read_csv(
                self.master_path +
                "/data/scps.csv",
                index_col=0)
        except FileNotFoundError as e:
            print(e)

        if brt in self.BRANCHS:
            result = result.query('branches in @brt')

        result = result.sample()

        result = result[0:1].values.tolist()
        result = itertools.chain(*result)
        result = list(result)

        await ctx.send(result[1] + "\n" + self.SCP_JP + result[0])

    @rand.error
    async def unknown_error_handler(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['mt'])
    @commands.has_permissions(kick_members=True)
    async def meeting(self, ctx, brt: typing.Optional[str] = 'all'):
        content = ""
        contentlist = lib.get_scp_rss(self.bot.meeting_addr)[0]
        title = contentlist[1]
        url = contentlist[0]
        text = contentlist[2].split("</p>")
        text = lib.tag_to_discord(text)

        embed = discord.Embed(
            title="本日の定例会テーマのお知らせです",
            url=url,
            color=0x0000a0)

        for x in text:
            content += x

        embed.add_field(
            name=title,
            value=content,
            inline=False)

        await ctx.send(embed=embed)

    @meeting.error
    async def unknown_error_handler(self, ctx, error):
        if discord.ext.commands.errors.MissingPermissions:
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['sh'])
    @commands.has_permissions(kick_members=True)
    async def shuffle(self, ctx, num: typing.Optional[int] = 2):
        settime = 10.0 * 60
        cnt = 4
        reaction_member = []
        emoji_in = '\N{THUMBS UP SIGN}'
        emoji_go = '\N{NEGATIVE SQUARED CROSS MARK}'

        embed = discord.Embed(title="下書き批評に参加するメンバーを募集します", colour=0x1e90ff)
        embed.add_field(
            name=f"参加する方はリアクション{emoji_in}を押してください",
            value="ご参加お待ちしております",
            inline=True)
        embed.set_footer(text='少し待ってからリアクションをつけてください')

        msg = await ctx.send(embed=embed)

        await msg.add_reaction(emoji_in)
        await msg.add_reaction(emoji_go)
        await asyncio.sleep(0.3)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=settime)
            except asyncio.TimeoutError:
                await ctx.send('タイムアウトしました')
                break
            else:
                if str(reaction.emoji) == emoji_go:
                    if ctx.author.id == user.id:
                        if len(reaction_member) < num:
                            await ctx.send('最低人数を満たしませんでした')
                            await msg.clear_reactions()
                            break

                        await ctx.send('募集を終了しました')

                        reaction_member = list(set(reaction_member))

                        random.shuffle(reaction_member)
                        divided_reaction_member = np.array_split(
                            reaction_member, num)

                        embed = discord.Embed(
                            title="割り振りは以下の通りです",
                            color=0x1e90ff)

                        for i in range(num):
                            str_member = '\n'.join(divided_reaction_member[i])
                            embed.add_field(
                                name=f'grop:{i}', value=f'{str_member}', inline=True)
                        embed.set_footer(text='よろしくお願いします')

                        await msg.edit(embed=embed)
                        await msg.clear_reactions()

                        break
                    else:
                        await msg.remove_reaction(str(reaction.emoji), user)

                elif str(reaction) == emoji_in:
                    if user.id in reaction_member:
                        pass
                    else:
                        reaction_member.append(user.mention)

    @shuffle.error
    async def unknown_error_handler(self, ctx, error):
        if discord.ext.commands.errors.MissingPermissions:
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['tm'])
    # @commands.has_permissions(kick_members=True)
    async def timer(self, ctx, num: typing.Optional[int] = 30):
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

        f = open(self.master_path + "/data/timer_dict.json", "w")
        json.dump(
            self.timer_dict,
            f,
            ensure_ascii=False,
            indent=4,
            separators=(
                ',',
                ': '))
        f.close()

        await ctx.send(f"{ctx.author.mention} : {num}分のタイマーを開始します")

    @timer.error
    async def unknown_error_handler(self, ctx, error):
        if discord.ext.commands.errors.MissingPermissions:
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def help(self, ctx):
        msg = discord.Embed(
            title='本BOTの使い方を説明させていただきます.',
            description='よろしくお願いします.' +
            ctx.author.mention,
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
        '''msg.add_field(
            name="/meeting(mt)",
            value="#scp-jp 定例会のお知らせスレッドから定例会のテーマを取得表示します.",
            inline=False)
        msg.add_field(
            name="/shuffle(sh) $num:default=2$",
            value="定例会の下書き批評回における振り分けを行います.(試験運用)",
            inline=False)'''
        msg.add_field(
            name="追記",
            value="バグ等を発見した場合は、然るべき場所にご報告ください.\n__**また、動作確認にはDMを使用することも可能です**__",
            inline=False)

        await ctx.send(embed=msg)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, message):
        print(message)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if all(s in ctx.content for s in [
               str(self.bot.user.id), '更新']):  # 要書き直し
            if ctx.author.id == self.bot.admin_id:
                await ctx.channel.send(self.bot.json_data['announce'])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 609058923353341973 or 286871252784775179:
            channel = self.bot.get_channel(member.guild._system_channel_id)
            await asyncio.sleep(3)
            embed = discord.Embed(
                title=f"{member.guild.name}へようこそ",
                colour=0x0080ff)
            embed.add_field(
                name=f"こんにちは,{member.name}.",
                value=f"<#548544598826287116>の確認ののち,<#464055645935501312>でアイサツをお願いします.",
                inline=True)
            # 文面考えてほしい
            embed.add_field(
                name=f"welcome {member.name}.",
                value=f"please check and read <#569530661350932481> and then give a reaction to this msg.",
                inline=True)
            embed.set_footer(text='読了したら何らかのリアクションをつけてください')
            await channel.send(member.mention)
            msg = await channel.send(embed=embed)

    @tasks.loop(seconds=30.0)
    async def multi_timer(self):
        now = datetime.now()
        for key in list(self.timer_dict.keys()):
            dict_time_just = datetime.strptime(
                self.timer_dict[key]['just'], '%Y-%m-%d %H:%M:%S')
            dict_time_m5 = datetime.strptime(
                self.timer_dict[key]['-5'], '%Y-%m-%d %H:%M:%S')

            if dict_time_just < now:
                mention = self.timer_dict[key]['author']
                channel = self.bot.get_channel(self.timer_dict[key]['channel'])
                await channel.send(f'時間です : {mention}')

                self.timer_dict.pop(key, None)

                f = open(self.master_path + "/data/timer_dict.json", "w")
                json.dump(
                    self.timer_dict,
                    f,
                    ensure_ascii=False,
                    indent=4,
                    separators=(
                        ',',
                        ': '))
                f.close()

            elif dict_time_m5 < now and self.timer_dict[key]['flag'] == 0:
                mention = self.timer_dict[key]['author']
                channel = self.bot.get_channel(self.timer_dict[key]['channel'])
                self.timer_dict[key]['flag'] = 1
                await channel.send(f'残り５分です : {mention}')

                f = open(self.master_path + "/data/timer_dict.json", "w")
                json.dump(
                    self.timer_dict,
                    f,
                    ensure_ascii=False,
                    indent=4,
                    separators=(
                        ',',
                        ': '))
                f.close()

    @multi_timer.before_loop
    async def before_timer(self):
        # print('booting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tachibana_Com(bot))
