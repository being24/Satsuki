# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import traceback
import typing
from datetime import datetime

import discord
import discosnow as ds
from discord.ext import commands, tasks


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        if not self.bot.loop.is_running():
            self.auto_backup.start()

    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        if cogname == "ALL":
            reloaded_list = []
            for cog in os.listdir(self.master_path + "/cogs"):
                if cog.endswith(".py"):
                    try:
                        cog = cog[:-3]
                        self.bot.reload_extension(f'cogs.{cog}')
                        reloaded_list.append(cog)
                    except Exception:
                        traceback.print_exc()
            await ctx.send(f"{reloaded_list}をreloadしました")
        else:
            try:
                self.bot.reload_extension(f'cogs.{cogname}')
                await ctx.send(f"{cogname}をreloadしました")
            except Exception as e:
                print(e)
                await ctx.send(e)

    @commands.command(aliases=['st'], hidden=True)
    async def status(self, ctx, word: str):
        await self.bot.change_presence(activity=discord.Game(name=word))
        await ctx.send(f"ステータスを{word}に変更しました")

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        start_time = time.time()
        mes = await ctx.send("Pinging....")
        await mes.edit(content="pong!\n" + str(round(time.time() - start_time, 3) * 1000) + "ms")

    @commands.command(aliases=['wh'], hidden=True)
    async def where(self, ctx):
        await ctx.send("現在入っているサーバーは以下です")
        servers = ",".join(g.name.replace('\u3000', ' ') for g in ctx.bot.guilds)
        await ctx.send(f"{servers}")

    @commands.command(aliases=['mem'], hidden=True)
    async def num_of_member(self, ctx):
        await ctx.send(f"{ctx.guild.member_count}")

    @commands.command(hidden=True)
    async def back_up(self, ctx):
        json_files = [
            filename for filename in os.listdir(self.master_path + "/data")
            if filename.endswith(".json")]

        my_files = [discord.File(f'{self.master_path}/data/{i}')
                    for i in json_files]

        await ctx.send(files=my_files)

    @commands.command(hidden=True)
    async def restore_one(self, ctx):
        for attachment in ctx.message.attachments:
            await attachment.save(f"{self.master_path}/data/{attachment.filename}")

    @commands.command(hidden=True)
    async def restore(self, ctx):
        async for message in ctx.channel.history(limit=100):
            if message.author.id != self.bot.user.id:
                continue
            if message.attachments:
                attachments_name = ' '.join(i.filename for i in message.attachments)
                msg_time = ds.snowflake2time(message.id).strftime('%m-%d %H:%M')
                await ctx.send(f'{msg_time}の{attachments_name}を取り込みます')
                for attachment in message.attachments:
                    await attachment.save(f"{self.master_path}/data/{attachment.filename}")
                break

    @tasks.loop(minutes=1.0)
    async def auto_backup(self):
        await self.bot.wait_until_ready()

        now = datetime.now()
        now_HM = now.strftime('%H:%M')

        if now_HM == '04:00':
            channel = self.bot.get_channel(745128369170939965)

            json_files = [filename for filename in os.listdir(self.master_path + "/data")if filename.endswith(".json")]
            my_files = [discord.File(f'{self.master_path}/data/{i}')for i in json_files]

            await channel.send(files=my_files)


def setup(bot):
    bot.add_cog(Admin(bot))
