# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_Tale(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    # serchコマンド
    @commands.group(aliases=['src'])
    async def search(self, ctx):
        # これ弄ったら多分サブコマンドない時―で分岐できるからscpのほうがハカドル
        if ctx.invoked_subcommand is None:
            await ctx.send('検索対象を指定してください？')  # SCP,TALE,AUTHER,HUB???

    @search.command()
    async def tale(self, ctx, brt: str, word: str):
        if brt not in BRANCHS:
            brt = "*"
        reply = lib.src("tale", brt, word)
        await ctx.send(reply)

    @tale.error
    async def tale_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> at src tale command\n{error}')

    # async def rand(self, ctx, num1: int, num2: typing.Optional[int] = 0):


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Tale(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
