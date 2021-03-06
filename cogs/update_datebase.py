# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import subprocess
import discord

import pandas as pd
from discord.ext import commands


class UpdateDataCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    def return_num_of_scp(self):
        dictionary = pd.DataFrame(
            columns=[
                'url',
                'title',
                'author',
                'branches'])
        try:
            dictionary = pd.read_csv(
                self.master_path +
                "/data/scps.csv",
                index_col=0)
        except FileNotFoundError as e:
            print(e)

        num_dict = {"all": len(dictionary)}

        BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn', 'cs',
                   'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']

        for brt in BRANCHS:
            num_dict[brt] = len(dictionary.query('branches in @brt'))

        return num_dict

    @commands.command(hidden=True)
    @commands.has_permissions(ban_members=True)
    async def update(self, ctx):
        await self.bot.change_presence(activity=discord.Game(name="更新中"))

        if os.name == "nt":
            await ctx.send("windows上でこのコマンドは使用できません")
        elif os.name == "posix":
            subprocess.Popen(self.master_path + "/ayame.sh")
        else:
            print("error")

        await self.bot.change_presence(activity=discord.Game(name=self.bot.status))

    @update.error
    async def update_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['num'], hidden=True)
    @commands.has_permissions(ban_members=True)
    async def num_of_scp(self, ctx):
        csv_dict = self.return_num_of_scp()
        await ctx.send(f"{csv_dict}")

    @num_of_scp.error
    async def num_of_scp_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):
    bot.add_cog(UpdateDataCog(bot))
