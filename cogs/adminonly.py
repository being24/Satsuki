# !/usr/bin/env python3
# -*- coding: utf-8 -*-



import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート



SCP_JP = "http://ja.scp-wiki.net"
BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']


class Tachibana_admin(commands.Cog):  # コグとして用いるクラスを定義。

    def __init__(self, bot):  # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)  # 権限変える
    async def update(self, ctx):
        await self.bot.change_presence(activity=discord.Game(name="更新中"))

        '''sys.path.append('../ayame')
        from ayame import tales, scips, proposal, guidehub, ex, author
        scips.scips()
        tales.tale()
        proposal.proposal()
        guidehub.guide_hub()
        ex.ex()
        author.author()
        await ctx.send('done')'''

        if os.name is "nt":
            await ctx.send("windows上でこのコマンドは使用できません")
        elif os.name is "posix":
            subprocess.Popen("./tachibana.sh")
        else:
            print("error")

        await self.bot.change_presence(activity=discord.Game(name=self.bot.status))

    @update.error
    async def update_error(self, ctx, error):
        await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):  # Bot本体側からコグを読み込む際に呼び出される関数。
    bot.add_cog(Tachibana_SCP(bot))  # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
