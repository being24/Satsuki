# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing
from datetime import datetime, timedelta

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_Com(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    @commands.command()  # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    async def draft(self, ctx):
        target_url = 'http://njr-sys.net/irc/draftReserve/'

        # d_today = (datetime.now() + timedelta(hours=-3)).date()
        d_today = '2019-10-12'
        response = requests.get(target_url + str(d_today))

        soup = BeautifulSoup(response.text, 'lxml')

        limen_object = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')
        print(limen_object)

        url = []
        time = []
        title = []
        author = []

        for i, detail in enumerate(soup.find_all(class_='irc-table__message')):            
            if i % 4 == 0:
                time_object = datetime.strptime(
                    f'{d_today}-{detail.string.replace(" ", "")}', '%Y-%m-%d-%H:%M:%S')
                if time_object < limen_object:
                    flag = 1
                else:
                    flag = 0
                    time.append(detail.string.replace(" ", ""))                
            elif i % 4 == 1:
                if flag == 0:
                    author.append(detail.string.replace(" ", ""))
            elif i % 4 == 2:
                if flag == 0:
                    title.append(detail.string.replace(" ", ""))
            else:
                if flag == 0:
                    url.append(detail.a.get("href"))

        if len(url) == 0:
            await ctx.send("本日の予約はありません")
            return

        embed = discord.Embed(
            title="下書き批評予約システムからデータを取得します",
            description=f"本日の下書き批評予約は全{len(url)}件です",
            color=0xff0080)

        for i in range(len(author)):
            embed.add_field(
                name=author[i],
                value=f"予約時間:{time[i]}\n{title[i]}\n{url[i]}",
                inline=False)

        embed.set_footer(text=f"受付開始時間外の予約は無効です")
        await ctx.send(embed=embed)

    @draft.error
    async def draft_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> at draft command\n{error}')

    # エラーキャッチ
    @commands.Cog.listener()
    async def on_command_error(self, ctx, message):
        print(message)


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Com(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
