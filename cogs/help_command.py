# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from discord import Embed
import discord
from discord.ext import commands
from discord.ext.commands.core import Group
from discord.ext.commands import Cog, command
from discord.ext.menus import ListPageSource, MenuPages
from discord.utils import get


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []
    sub_commands = []
    sub_command_str = ''

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(
                f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    if isinstance(command, Group):
        for sub_command in command.commands:
            sub_command_str = f'{sub_command.name.ljust(7)} | {" ".join(sub_command.aliases)}'
            for key, value in sub_command.params.items():
                if key not in ("self", "ctx"):
                    sub_command_arg = f"[{key}]" if "NoneType" in str(
                        value) else f"<{key}>"
                    sub_command_str = f'{sub_command_str} {sub_command_arg}'

            sub_commands.append(sub_command_str)

    params = " ".join(params)

    sub_commands = "\n  - ".join(sub_commands)

    if len(sub_commands) == 0:
        return f"`{cmd_and_aliases} {params}`"
    else:
        return f"`{cmd_and_aliases} {params}`\n\nサブコマンド\n`  - {sub_commands}`"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=6)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="コマンド一覧",
                      description=f"使用可能なコマンド : {self.ctx.author.mention}",
                      colour=self.ctx.author.colour)

        if self.ctx.author.avatar is None:
            avatar_url = 'https://cdn.discordapp.com/embed/avatars/0.png'
        else:
            avatar_url = self.ctx.author.avatar.replace(format="png").url

        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append(
                (entry.description or "No Description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Help with `{command}` : {ctx.author.name}",
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @ command(name="help", description='リアクション式ヘルプコマンド')
    async def help(self, ctx, *args: str):
        """拡張版ヘルプコマンド"""

        show_commands = [
            my_command for my_command in self.bot.commands if not my_command.hidden]

        show_commands = sorted(show_commands, key=lambda x: x.cog_name.lower())

        if (arg_len := len(args)) == 0:
            menu = MenuPages(source=HelpMenu(ctx, show_commands),
                             delete_message_after=False,
                             clear_reactions_after=True,
                             timeout=60.0)
            await menu.start(ctx)

        else:
            if (command := get(self.bot.commands, name=args[0])):
                if isinstance(command, Group):
                    if arg_len == 1:
                        await self.cmd_help(ctx, command)

                    else:
                        if (sub_command := get(
                                command.commands, name=args[1])):
                            await self.cmd_help(ctx, sub_command)
                        else:
                            await ctx.send("**Command error**: `subcommand not found`")

                else:
                    await self.cmd_help(ctx, command)

            else:
                await ctx.send("**Command error**: `command not found`")


def setup(bot):
    bot.add_cog(Help(bot))
