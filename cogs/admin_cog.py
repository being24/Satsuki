# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import typing

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        if cogname == "ALL":
            for cog in self.bot.INITIAL_COGS:
                try:
                    self.bot.unload_extension(f'cogs.{cog}')
                    self.bot.load_extension(f'cogs.{cog}')
                except Exception as e:
                    print(e)
            await ctx.send(f"{self.bot.INITIAL_COGS}をreloadしました")
        else:
            try:
                self.bot.unload_extension(f'cogs.{cogname}')
                self.bot.load_extension(f'cogs.{cogname}')
                await ctx.send(f"{cogname}をreloadしました")
            except Exception as e:
                print(e)
                await ctx.send(e)

    @commands.command(aliases=['st'], hidden=True)
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
        await mes.edit(content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms")

    @commands.command(aliases=['wh'], hidden=True)
    async def where(self, ctx):
        await ctx.send("現在入っているサーバーは以下です")
        server_list = [i.name.replace('\u3000', ' ')
                       for i in ctx.bot.guilds]
        await ctx.send(f"{server_list}")

    @commands.command(aliases=['mem'], hidden=True)
    async def num_of_member(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")

    @commands.command(aliases=['send'], hidden=True)
    async def send_json(self, ctx):
        json_files = [
            filename for filename in os.listdir(self.master_path + "/data")
            if filename.endswith(".json")]

        my_files = [discord.File(f'{self.master_path}/data/{i}')
                    for i in json_files]

        await ctx.send(files=my_files)

    @commands.command(aliases=['receive'], hidden=True)
    async def receive_json(self, ctx):
        for attachment in ctx.message.attachments:
            await attachment.save(f"{self.master_path}/data/{attachment.filename}")


def setup(bot):
    bot.add_cog(Admin(bot))
