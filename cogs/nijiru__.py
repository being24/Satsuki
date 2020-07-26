# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import typing

import discord
from discord.ext import commands

import libs as lib


class NijiruAlter(commands.Cog, name='煮汁代替定例会予約'):
    def __init__(self, bot):
        self.bot = bot
        self.SB_URL = (
            "http://scp-jp-sandbox3.wikidot.com/",
            "http://scp-jp-sandbox2.wikidot.com/")

    @commands.command(aliases=['reserv'], enabled=False)
    async def reservation(self, ctx, title, url=None):
        if url is None:
            await ctx.send("引数が不足しています.")
            pass
        if url.startswith(self.SB_URL):
            # 空白でsplit、URLとそれ以外を分けそれ以外の最初をタイトルにする！
            await ctx.send(f"title : **{title}** {url} にて\n{ctx.message.created_at}に予約を受け付けました．")
        else:
            print("False")


def setup(bot):
    bot.add_cog(NijiruAlter(bot))
