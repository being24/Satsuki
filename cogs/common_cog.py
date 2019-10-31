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
import pandas as pd
import requests
from bs4 import BeautifulSoup
from discord.ext import commands  # Bot Commands Frameworkのインポート
from pytz import timezone

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn', 'cs',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_Com(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot
        self.SCP_JP = "http://ja.scp-wiki.net"
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    @commands.command(aliases=['p'])  # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command(aliases=['df'])
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

        if int(nums[1]) > 10000:
            await ctx.send("入力値が大きすぎです")

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

        if brt in BRANCHS:
            result = result.query('branches in @brt')

        result = result.sample()

        result = result[0:1].values.tolist()
        result = itertools.chain(*result)
        result = list(result)

        await ctx.send(result[1] + "\n" + SCP_JP + result[0])

    @rand.error
    async def unknown_error_handler(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['mt'])
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
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['sh'])
    @commands.has_permissions(ban_members=True)
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
        await asyncio.sleep(1)

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
                        random.shuffle(reaction_member)
                        divided_reaction_member = [
                            reaction_member[i::num] for i in range(num)]

                        embed = discord.Embed(
                            title="割り振りは以下の通りです",
                            color=0x1e90ff)
                        for i in range(num):
                            embed.add_field(
                                name=f'{i}', value=f'<@{reaction_member[i]}>', inline=True)
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
                        reaction_member.append(user.id)

    @shuffle.error
    async def unknown_error_handler(self, ctx, error):
        # '\N{THUMBS UP SIGN}'
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

        # エラーキャッチ
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


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Com(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
