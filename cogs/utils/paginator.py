# ===== Credit =====
# プロジェクト名: kanri-chan
# URL: https://github.com/ichidaisai/kanri-chan/blob/main/app/mylib/pagenator.py
# ライセンス: BSD 3-Clause License
# 著作権者: 広島市立大学 大学祭
# 著者: Huyu2239
#
# 以下のコードはBSD 3-Clause Licenseに従って利用し、Alpaca131が改変しています。
# ===== Credit =====

from __future__ import annotations

import discord
from discord.ext import commands


class Paginator(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        embed: discord.Embed,
        initial_page: int = 0,
        field_threshold: int = 25,
        allow_non_author_interaction: bool = False,
        ephemeral: bool = False,
    ):
        super().__init__(timeout=120)
        self.threshold = field_threshold
        self.embed_pages = self._split_embed(embed)
        self.ctx = ctx
        self.initial_page = initial_page
        self.allow_non_author_interaction = allow_non_author_interaction
        self.ephemeral = ephemeral

        self.total_page_count = len(self.embed_pages)
        self.current_page = self.initial_page
        self.message = None

        self.back_button = discord.ui.Button(
            emoji=discord.PartialEmoji(name="\U000025c0")
        )
        self.next_button = discord.ui.Button(
            emoji=discord.PartialEmoji(name="\U000025b6")
        )
        self.page_counter_style = discord.ButtonStyle.grey
        self.back_button.callback = self.back_button_callback
        self.next_button.callback = self.next_button_callback
        self.page_counter = PageCounter(
            style=self.page_counter_style,
            total_page_count=self.total_page_count,
            initial_page=self.initial_page,
        )
        self.add_item(self.back_button)
        self.add_item(self.page_counter)
        self.add_item(self.next_button)

    async def start(self):
        self.message = await self.ctx.send(
            embed=self.embed_pages[self.initial_page],
            view=self,
            ephemeral=self.ephemeral,
        )

    async def go_back(self):
        self.current_page = (self.current_page - 1) % self.total_page_count
        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embed=self.embed_pages[self.current_page], view=self)

    async def go_next(self):
        self.current_page = (self.current_page + 1) % self.total_page_count
        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embed=self.embed_pages[self.current_page], view=self)

    async def next_button_callback(self, interaction):
        if interaction.user != self.ctx.author and self.allow_non_author_interaction:
            embed = discord.Embed(
                description="実行者のみ操作可能です。",
                color=discord.Colour.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.go_next()
        await interaction.response.defer()

    async def back_button_callback(self, interaction):
        if interaction.user != self.ctx.author and self.allow_non_author_interaction:
            embed = discord.Embed(
                description="実行者のみ操作可能です。",
                color=discord.Colour.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.go_back()
        await interaction.response.defer()

    def _split_embed(self, embed: discord.Embed):
        embeds = []

        def _create_embed():
            _embed = discord.Embed(
                title=embed.title, description=embed.description, color=embed.colour
            )
            _embed.set_footer(text=embed.footer.text)
            _embed.set_thumbnail(url=embed.thumbnail.url)
            _embed.set_image(url=embed.image.url)
            _embed.timestamp = embed.timestamp
            _embed.url = embed.url
            return _embed

        current_embed = _create_embed()
        for field in embed.fields:
            # compare to the smaller one
            if len(current_embed.fields) < min(self.threshold, 25):
                current_embed.add_field(
                    name=field.name, value=field.value, inline=field.inline
                )
            else:
                embeds.append(current_embed)
                current_embed = _create_embed()
                current_embed.add_field(
                    name=field.name, value=field.value, inline=field.inline
                )
            continue
        embeds.append(current_embed)
        return embeds

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(embed=self.embed_pages[self.current_page], view=self)


class PageCounter(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, total_page_count, initial_page):
        super().__init__(
            label=f"{initial_page + 1}/{total_page_count}", style=style, disabled=True
        )
