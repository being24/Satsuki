# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import subprocess
import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート


def is_in_guild():
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == 609058923353341973
    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 277825292536512513
    return commands.check(predicate)


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    @commands.command(aliases=['re'], hidden=True)
    @is_owner()
    @is_in_guild()
    async def reload(self, ctx):
        for cog in self.bot.INITIAL_COGS:
            try:
                self.bot.unload_extension(f"{cog}")
                self.bot.load_extension(f"{cog}")
                await ctx.send(f"{cog} reloaded")
            except Exception as e:
                print(e)

    @reload.error
    async def reload_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['st'], hidden=True)
    @is_owner()
    @is_in_guild()
    async def status(self, ctx, word: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.send(f"ステータスを{word}に変更しました")
            self.bot.status = word
        except BaseException:
            pass

    @status.error
    async def status_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        await ctx.send('pong!')


def setup(bot):
    bot.add_cog(admin(bot))
