# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command
from discord.ext.menus import ListPageSource, MenuPages
from discord.utils import get


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(
                f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"`{cmd_and_aliases} {params}`"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="コマンド一覧",
                      description="使用可能なコマンド",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        entries = sorted(entries, key=lambda x: x.cog_name.lower())
        for entry in entries:
            fields.append(
                (entry.description or "No Description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Help with `{command}`",
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @command(name="ac_help", description='ヘルプコマンド')
    async def ac_help(self, ctx, cmd: Optional[str]):
        """拡張版ヘルプコマンド"""
        show_commands = [
            my_command for my_command in self.bot.commands if not my_command.hidden]
        if cmd is None:
            menu = MenuPages(source=HelpMenu(ctx, show_commands),
                             delete_message_after=True,
                             timeout=60.0)
            await menu.start(ctx)

        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send("**Command error**: `command not found`")


def setup(bot):
    bot.add_cog(Help(bot))
