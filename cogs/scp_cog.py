# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import discord
from discord.ext import commands

import libs as lib


class SatsukiSCPCog(commands.Cog, name='SCPコマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://scp-jp.wikidot.com"

    @commands.command()
    async def scp(self, ctx, *, num_brt):
        num_brt = num_brt.replace(" ", "")
        reply = lib.scp_number(num_brt)
        if reply is not None:
            if isinstance(reply, str):
                await ctx.send(reply)
            else:
                await ctx.send(reply[1] + "\n" + self.SCP_JP + reply[0])


def setup(bot):
    bot.add_cog(SatsukiSCPCog(bot))
