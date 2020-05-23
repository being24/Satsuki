# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import typing

import discord
from discord.ext import commands


def is_double_owner():  # botのオーナーかつサーバー主のみが実行できるコマンド
    async def predicate(ctx):
        return ctx.guild and ctx.author.id == ctx.guild.owner_id \
            and ctx.author.id == ctx.bot.admin_id
    return commands.check(predicate)


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    @commands.Cog.listener()
    async def on_ready(self):
        self.owner_data = await self.bot.application_info()

    @commands.group(aliases=['re'], hidden=True)
    @is_double_owner()
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        reloaded_cogs = []
        if cogname == "ALL":
            for cog in self.bot.INITIAL_COGS:
                try:
                    self.bot.unload_extension(f'cogs.{cog}')
                    self.bot.load_extension(f'cogs.{cog}')
                    reloaded_cogs.append(cog)
                except Exception as e:
                    print(e)
            reloaded_cogs = '\n'.join(reloaded_cogs)
            await ctx.send(f"{reloaded_cogs}")
            await ctx.send("\n上記cogをreloadしました")
        else:
            try:
                self.bot.unload_extension(f'cogs.{cogname}')
                self.bot.load_extension(f'cogs.{cogname}')
                await ctx.send(f"{cogname}をreloadしました")
            except Exception as e:
                print(e)
                await ctx.send(e)

    @commands.command(aliases=['st'], hidden=True)
    @is_double_owner()
    async def status(self, ctx, word: str):
        try:
            await self.bot.change_presence(activity=discord.Game(name=word))
            await ctx.send(f"ステータスを{word}に変更しました")
        except BaseException:
            pass

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        start_time = time.time()
        mes = await ctx.send("Pinging....")
        latency = str(round(time.time() - start_time, 3) * 1000)
        await mes.edit(content=f"pong!\n{latency}ms")

    @commands.command(aliases=['wh'], hidden=True)
    @is_double_owner()
    async def where(self, ctx):
        guild_list = []
        await ctx.send("現在入っているサーバーは以下の通りです")
        for s in ctx.cog.bot.guilds:
            guild_list.append(s.name.replace('\u3000', ' '))
        guild_list = '\n'.join(guild_list)
        await ctx.send(f"{guild_list}")

    @commands.command(aliases=['mem'], hidden=True)
    @is_double_owner()
    async def num_of_member(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")


def setup(bot):
    bot.add_cog(admin(bot))
