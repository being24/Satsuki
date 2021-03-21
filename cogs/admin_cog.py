# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import time
import traceback
import typing
from datetime import datetime

import discord
import discosnow as ds
from discord.ext import commands, tasks

from cogs.utils.setting_manager import SettingManager


class Admin(commands.Cog, name='管理用コマンド群'):
    """
    管理用のコマンドです
    """

    def __init__(self, bot):
        self.bot = bot

        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        self.auto_backup.stop()
        self.auto_backup.start()
        self.setting_mng = SettingManager()

    async def cog_check(self, ctx):
        return ctx.guild and await self.bot.is_owner(ctx.author)

    @staticmethod
    def log_remove_guild(guild):
        error_content = f'サーバーを退出しました\nreason: black list\ndetail : {guild}'
        logging.error(error_content, exc_info=True)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setting_mng.create_table()
        guild_ids = [guild.id for guild in self.bot.guilds]
        await self.setting_mng.init_guilds(guild_ids)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """on_guild_join時に発火する関数
        """
        if guild_setting := await self.setting_mng.get_guild(guild.id):
            if guild_setting.black_server:
                await guild.leave()
                self.log_remove_guild(guild)
                return
        else:
            await self.setting_mng.register_guild(guild_id=guild.id)

        embed = discord.Embed(
            title="サーバーに参加しました",
            description=f"SCP公式チャット用utility-bot {self.bot.user.display_name}",
            color=0x2fe48d)
        embed.set_author(
            name=f"{self.bot.user.name}",
            icon_url=f"{self.bot.user.avatar_url}")
        await guild.system_channel.send(embed=embed)

    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, cogname: typing.Optional[str] = "ALL"):
        """Cogをリロードする関数
        """
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

    @commands.command(hidden=True)
    async def add_black_list(self, ctx, server_id: int):
        guild = self.bot.get_guild(ctx.guild.id)
        if guild is None:
            await ctx.reply(f'サーバーid : {server_id}を発見できませんでした')
            return

        await guild.leave()
        self.log_remove_guild(guild)
        if not await self.setting_mng.is_exist(server_id):
            await ctx.reply(f'サーバーid : {server_id}をDB上に発見できませんでした')
        else:
            await self.setting_mng.set_black_list(server_id)
            await ctx.reply(f'サーバー : {guild}を退出しました')

    @commands.command(hidden=True)
    async def remove_black_list(self, ctx, server_id: int):
        if not await self.setting_mng.is_exist(server_id):
            await ctx.reply(f'サーバーid : {server_id}をDB上に発見できませんでした')
        else:
            await self.setting_mng.remove_black_list(server_id)
            await ctx.reply(f'サーバー : {server_id}をブラックリストから除去しました')

    @commands.command(aliases=['p'], hidden=True)
    async def ping(self, ctx):
        """Pingによる疎通確認を行うコマンド"""
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
        """そのサーバーに何人いるかを確認する関数
        """

    @commands.command(hidden=True)
    async def back_up(self, ctx):
        """バックアップファイルを送信する関数
        """
        json_files = [
            filename for filename in os.listdir(self.master_path + "/data")
            if filename.endswith(".json")]

        my_files = [discord.File(f'{self.master_path}/data/{i}')
                    for i in json_files]

        await ctx.send(files=my_files)

    @commands.command(hidden=True)
    async def restore_one(self, ctx):
        """添付メッセージからファイルを取得する関数
        """
        for attachment in ctx.message.attachments:
            await attachment.save(f"{self.master_path}/data/{attachment.filename}")

    @commands.command(hidden=True)
    async def restore(self, ctx):
        """バックアップチャンネルからファイルを取得する関数
        """
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
