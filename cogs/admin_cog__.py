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

    @commands.group(aliases=['re'], hidden=True)
    @is_owner()
    @is_in_guild()
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        if cogname is "ALL":
            for cog in self.bot.INITIAL_COGS:
                try:
                    self.bot.unload_extension(f'cogs.{cog}')
                    self.bot.load_extension(f'cogs.{cog}')
                except Exception as e:
                    print(e)
            await ctx.send(f"{(self.bot.INITIAL_COGS)}をreloadしました")
        else:
            try:
                self.bot.unload_extension(f'cogs.{cogname}')
                self.bot.load_extension(f'cogs.{cogname}')
                await ctx.send(f"{cogname}をreloadしました")
            except Exception as e:
                print(e)
                await ctx.send(e)

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

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command(aliases=['wh'], hidden=True)
    @is_owner()
    async def where(self, ctx):
        await ctx.send("現在入っているサーバーは以下です")
        for s in ctx.cog.bot.guilds:
            await ctx.send(f"{s}")

    @commands.command(aliases=['mem'], hidden=True)
    @is_owner()
    async def num_of_member(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")


def setup(bot):
    bot.add_cog(admin(bot))
