# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート


class Tachibana_Cog(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    @commands.command()  # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    async def what(self, ctx, what: str):
        await ctx.send(f'{what}とはなんですか？')

    # serchコマンド
    @commands.group()
    async def serch(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('検索対象を指定してください？')

    # scp
    @serch.command()
    async def what(self, ctx, amount: typing.Optional[int] = 99):
        await ctx.send(f'{amount}とはなんですか？')

    # tale
    @serch.command()
    async def tale(self, ctx, word: str):
        if ctx.invoked_subcommand is None:
            print("err")
        else:
            await ctx.send('tale!')


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Cog(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
