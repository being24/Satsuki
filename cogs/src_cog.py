# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import typing

import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート

import libs as lib

SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_Tale(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot
        self.URL = "http://ja.scp-wiki.net"

    # serchコマンド
    @commands.group(aliases=['src'])
    async def search(self, ctx):
        # これ弄ったら多分サブコマンドない時―で分岐できるからscpのほうがハカドル
        if ctx.invoked_subcommand is None:
            await ctx.send('検索対象を指定してください')  # SCP,TALE,AUTHER,HUB???

    @search.command()
    async def tale(self, ctx,  word: str):
        '''if brt not in BRANCHS:
            brt = "*"
        '''
        reply = lib.src_tale(word)

        if len(reply) > 10:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="TALE検索結果",
            description=f"検索ワード'{word}'にヒットしたTaleは{len(reply)}件です。",
            color=0xff8000)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=self.URL + line[1] + "\nAuthor : " + line[3],
                inline=False)

        embed.set_footer(text="タイトル、URL、著者名から検索しています。")
        await ctx.send(embed=embed)

    @tale.error
    async def tale_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> at tale command\n{error}')

    @search.command()
    async def proposal(self, ctx, word: str):

        reply = lib.src_proposal(word)

        if len(reply) > 10:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="提言検索結果",
            description=f"検索ワード'{word}'にヒットした提言は{len(reply)}件です。",
            color=0x0080c0)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています。")
        await ctx.send(embed=embed)

    @proposal.error
    async def proposal_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> at proposal command\n{error}')


    @search.command()
    async def joke(self, ctx, word: str):

        reply = lib.src_joke(word)

        if len(reply) > 10:
            await ctx.send(f"ヒット{len(reply)}件、多すぎます")
            return

        embed = discord.Embed(
            title="joke検索結果",
            description=f"検索ワード'{word}'にヒットしたjokeは{len(reply)}件です。",
            color=0x800080)

        for line in reply.itertuples():
            embed.add_field(
                name=line[2],
                value=f"{self.URL}{line[1]}",
                inline=False)

        embed.set_footer(text="タイトル、URLから検索しています。")
        await ctx.send(embed=embed)

    @joke.error
    async def joke_error(self, ctx, error):
        await ctx.send(f'to <@277825292536512513> at joke command\n{error}')

    # async def rand(self, ctx, num1: int, num2: typing.Optional[int] = 0):


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_Tale(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
