# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing

import discord
from discord.ext import commands

import libs as lib


class Tachibana_SCP(commands.Cog, name='SCPコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://ja.scp-wiki.net"

    @commands.command()
    async def scp(self, ctx, *, num_brt):
        num_brt = num_brt.replace(" ", "")
        reply = lib.scp_number(num_brt)
        if reply is not None:
            if isinstance(reply, str):
                await ctx.send(reply)
            else:
                await ctx.send(reply[1] + "\n" + self.SCP_JP + reply[0])

    @scp.error
    async def scp_error(self, ctx, error):
        if discord.ext.commands.errors.BadArgument:
            await ctx.send('入力値が不正です')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):
    bot.add_cog(Tachibana_SCP(bot))
