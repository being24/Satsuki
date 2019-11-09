# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import subprocess
import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


def is_in_guild():
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == 609058923353341973
    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 277825292536512513
    return commands.check(predicate)


class Tachibana_admin(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    @is_in_guild()
    async def update(self, ctx):
        await self.bot.change_presence(activity=discord.Game(name="更新中"))

        '''sys.path.append('../ayame')
        from ayame import tales, scips, proposal, guidehub, ex, author
        scips.scips()
        tales.tale()
        proposal.proposal()
        guidehub.guide_hub()
        ex.ex()
        author.author()
        await ctx.send('done')'''

        if os.name is "nt":
            await ctx.send("windows上でこのコマンドは使用できません")
        elif os.name is "posix":
            subprocess.Popen("./tachibana.sh")  # currentpath使わんと
        else:
            print("error")

        await self.bot.change_presence(activity=discord.Game(name=self.bot.status))

    @update.error
    async def update_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['re'], hidden=True)
    @is_owner()
    @is_in_guild()
    async def reload(self, ctx, module: str):
        await self.bot.change_presence(activity=discord.Game(name="更新中"))

        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            await ctx.send(f"{module} reloaded")
        except Exception as e:
            print(e)

        await self.bot.change_presence(activity=discord.Game(name=self.bot.status))

    @reload.error
    async def reload_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['sta'], hidden=True)
    @commands.has_permissions(kick_members=True)
    async def statistics(self, ctx):
        csv_dict = lib.statistics_csv()
        await ctx.send(f"{csv_dict}")

    @statistics.error
    async def statistics_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_admin(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
