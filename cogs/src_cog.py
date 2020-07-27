# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib


class SatsukiSRCCog(commands.Cog, name='検索コマンド'):  # コグとして用いるクラスを定義
    def __init__(self, bot):  # TestCogクラスのコンストラクタBotを受取り、インスタンス変数として保持
        self.bot = bot
        self.URL = "http://scp-jp.wikidot.com"

    @commands.command()
    async def tale(self, ctx, word: str):
        reply = lib.src_tale(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="TALE検索結果",
            description=f"検索ワード'{word}'にヒットしたTaleは{len(reply)}件です",
            color=0xff8000)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=self.URL + line[1] + "\nAuthor : " + line[3],
                inline=False)

        embed.set_footer(text="タイトル、URL、著者名から検索しています")
        await ctx.send(embed=embed)

    @commands.command(aliases=['prop'])
    async def proposal(self, ctx, word: str):
        reply = lib.src_proposal(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="提言検索結果",
            description=f"検索ワード'{word}'にヒットした提言は{len(reply)}件です",
            color=0x0080c0)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています")
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx, word: str):
        reply = lib.src_joke(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="joke検索結果",
            description=f"検索ワード'{word}'にヒットしたjokeは{len(reply)}件です",
            color=0x800080)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています")
        await ctx.send(embed=embed)

    @commands.command(aliases=['gd', 'rtfm'])
    async def guide(self, ctx, word: str = None):
        if word is None:
            return await ctx.send('引数が必要です')
        reply = lib.src_guide(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="ガイド検索結果",
            description=f"検索ワード'{word}'にヒットしたガイドは{len(reply)}件です",
            color=0x800080)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています")
        await ctx.send(embed=embed)

    @commands.command(aliases=['auth'])
    async def author(self, ctx, word: str):
        reply = lib.src_author(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="著者ページ検索結果",
            description=f"検索ワード'{word}'にヒットした著者ページは{len(reply)}件です",
            color=0x8000ff)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="著者名から検索しています")
        await ctx.send(embed=embed)

    @commands.command(aliases=['ex'])
    async def explained(self, ctx, word: str):
        reply = lib.src_explained(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="explained検索結果",
            description=f"検索ワード'{word}'にヒットしたexplainedは{len(reply)}件です",
            color=0x000080)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています")
        await ctx.send(embed=embed)

    @commands.command(aliases=['src'])
    async def search(self, ctx, word: str):
        reply = lib.src_scp(word)

        if len(reply) > self.bot.send_max:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="メタタイトル検索結果",
            description=f"検索ワード'{word}'にヒットしたSCPは{len(reply)}件です",
            color=0x00ff00)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=self.URL + line[1],
                inline=False)

        embed.set_footer(text="タイトルから検索しています")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SatsukiSRCCog(bot))
