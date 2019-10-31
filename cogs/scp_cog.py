# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_SCP(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    # サブコマンドがなかったらnumber検索、そうじゃなかったら検索にするか→いやsrcはsrcにしとこう
    @commands.command()
    async def scp(self, ctx, *, num_brt):
        num_brt = num_brt.replace(" ", "")
        reply = lib.scp_number(num_brt)
        if reply is not None:
            if isinstance(reply, str):
                await ctx.send(reply)
            else:
                await ctx.send(reply[1] + "\n" + SCP_JP + reply[0])

    @scp.error
    async def scp_error(self, ctx, error):
        if discord.ext.commands.errors.BadArgument:
            await ctx.send('入力値が不正です')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_SCP(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
