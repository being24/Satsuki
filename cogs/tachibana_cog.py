# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"


class Tachibana_Cog(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    @commands.command()  # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command()
    async def scp(self, ctx, *, num_brt):
        num_brt = num_brt.replace(" ", "")
        reply = lib.scp_number(self, num_brt)
        if reply is not None:
            if isinstance(reply, str):
                await ctx.send(reply)
            else:
                await ctx.send(reply[1] + "\n" + SCP_JP + reply[0])

    @scp.error
    async def scp_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> an error occurred\n{error}')

    # serchコマンド
    @commands.group()
    async def serch(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('検索対象を指定してください？')

    # tale
    @serch.command()
    async def tale(self, ctx, word: str):
        if ctx.invoked_subcommand is None:
            print("err")
        else:
            await ctx.send('tale!')


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Cog(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
