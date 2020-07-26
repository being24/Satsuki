# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import html
import os
import random
import re
import typing
from datetime import datetime, timedelta

import discord
import feedparser
import numpy as np
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


def get_scp_rss(target):
    feed_data = feedparser.parse(target)
    scp_rss = []
    for entries in feed_data['entries']:
        title = (entries['title'])
        link = (entries['link'])
        text = entries["content"][0]['value']
        scp_rss.append([link, title, text])
    return scp_rss


def tag_to_discord(content):
    result = []
    for line in content:
        line = line.replace("<p>", "\n")
        line = line.replace("</p>", "\n")
        line = line.replace("</div>", "")

        line = line.replace("<br />", "\n")

        if '<span class="rt">' in line:  # ルビ
            siz0_0 = line.find('<span class="rt">')
            siz0_1 = line.find('</span>', siz0_0 + 1)
            line = line.replace('<span class="rt">', " - [")
            line = line.replace('</span></span>', "]")  # 多分ここ違う

        if '<strong>' in line:  # 強調
            line = line.replace('<strong>', "**")
            line = line.replace('</strong>', "**")

        if '<span style="text-decoration: line-through;">' in line:  # 取り消し
            line = line.replace(
                '<span style="text-decoration: line-through;">', "~~")
            line = line.replace('</span>', "~~ ", 1)

        if '<span style="text-decoration: underline;">' in line:  # 下線
            line = line.replace(
                '<span style="text-decoration: underline;">', "__")
            line = line.replace('</span>', "__ ", 1)

        if '<em>' in line:  # 斜体
            line = line.replace('<em>', "*")
            line = line.replace('</em>', "*")

        if 'href' in line:
            match = re.findall(r'href=[\'"]?([^\'" >]+)', line)
            if len(match) == 0:
                line = ""
            elif "javascript" in match[0]:
                line = ""

            if len(match) != 0:
                deco_f = ' ['
                deco_b = f"]({match[0]}) "

            p = re.compile(r"<[^>]*?>")
            line = p.sub(f"{deco_b}", line)
            line = line.replace(deco_b, deco_f, 1)

        line = html.unescape(line)
        result.append(line)

    return result


class CritiqueCog(commands.Cog, name='批評定例会用コマンド'):
    def __init__(self, bot):
        self.bot = bot
        self.SCP_JP = "http://scp-jp.wikidot.com"
        self.master_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        self.BRANCHS = [
            'jp', 'en', 'ru', 'ko', 'es', 'cn', 'cs', 'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo'
        ]  # 外部に依存させたいな

    @commands.command(aliases=['df'])
    @commands.has_permissions(kick_members=True)
    async def draft(self, ctx, num: typing.Optional[int] = 0):
        target_url = 'http://njr-sys.net/irc/draftReserve/'

        d_today = (datetime.now() + timedelta(hours=-3)).date()
        # d_today = '2019-10-12'
        response = requests.get(target_url + str(d_today))

        soup = BeautifulSoup(response.text, "html.parser")

        limen_object = datetime.strptime(
            f'{d_today}-20:45:00', '%Y-%m-%d-%H:%M:%S')

        url = []
        time = []
        title = []
        author = []

        for i, detail in enumerate(soup.find_all(class_='irc-table__message')):
            if i % 4 == 0:
                time_object = datetime.strptime(
                    f'{d_today}-{detail.string.replace(" ", "")}',
                    '%Y-%m-%d-%H:%M:%S')
                if time_object < limen_object:
                    flag = 0
                else:
                    flag = 1
                    time.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 1:
                if detail.string is None:
                    author.append("None")
                else:
                    author.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 2:
                if detail.string is None:
                    title.append("None")
                else:
                    title.append(detail.string.replace(" ", ""))
            elif i % 4 * flag == 3:
                if detail.string is None:
                    url.append("None")
                else:
                    url.append(detail.a.get("href"))
            else:
                pass

        if len(url) == 0:
            await ctx.send("本日の予約はありません")
            return

        title_message = "下書き批評予約システムからデータを取得します"

        if num == 0:
            embed = discord.Embed(
                title=title_message,
                description=f"本日の下書き批評予約は全{len(url)}件です",
                color=0xff0080)

            for i in range(len(author)):
                embed.add_field(
                    name=author[i],
                    value=f'{i+1} : [{title[i]}]({url[i]})\tat: {time[i]}',
                    inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title=title_message,
                description=f"{num}/{len(url)}件目の下書きです",
                color=0xff0080)
            num = num - 1
            embed.add_field(
                name=author[num],
                value=f'{num+1} : [{title[num]}]({url[num]})\tat: {time[num]}',
                inline=False)

            embed.set_footer(text="受付時間外の予約は無効です!")
            await ctx.send(embed=embed)

    @draft.error
    async def draft_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['mt'])
    @commands.has_permissions(kick_members=True)
    async def meeting(self, ctx, brt: typing.Optional[str] = 'all'):
        content = ""
        contentlist = get_scp_rss(self.bot.meeting_addr)[0]
        title = contentlist[1]
        url = contentlist[0]
        text = contentlist[2].split("</p>")
        text = tag_to_discord(text)

        embed = discord.Embed(
            title="本日の定例会テーマのお知らせです",
            url=url,
            color=0x0000a0)

        for x in text:
            content += x

        embed.add_field(
            name=title,
            value=content,
            inline=False)

        await ctx.send(embed=embed)

    @meeting.error
    async def unknown_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')

    @commands.command(aliases=['sh'])
    @commands.has_permissions(kick_members=True)
    async def shuffle(self, ctx, num: typing.Optional[int] = 2):
        settime = 10.0 * 60
        reaction_member = []
        emoji_in = '\N{THUMBS UP SIGN}'
        emoji_go = '\N{NEGATIVE SQUARED CROSS MARK}'

        embed = discord.Embed(title="下書き批評に参加するメンバーを募集します", colour=0x1e90ff)
        embed.add_field(
            name=f"参加する方はリアクション{emoji_in}を押してください",
            value="ご参加お待ちしております",
            inline=True)
        embed.set_footer(text='少し待ってからリアクションをつけてください')

        msg = await ctx.send(embed=embed)

        await msg.add_reaction(emoji_in)
        await msg.add_reaction(emoji_go)
        await asyncio.sleep(0.3)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=settime)
            except asyncio.TimeoutError:
                await ctx.send('タイムアウトしました')
                break
            else:
                if str(reaction.emoji) == emoji_go:
                    if ctx.author.id == user.id:
                        if len(reaction_member) < num:
                            await ctx.send('最低人数を満たしませんでした')
                            await msg.clear_reactions()
                            break

                        await ctx.send('募集を終了しました')

                        reaction_member = list(set(reaction_member))

                        random.shuffle(reaction_member)
                        divided_reaction_member = np.array_split(
                            reaction_member, num)

                        embed = discord.Embed(
                            title="割り振りは以下の通りです",
                            color=0x1e90ff)

                        for i in range(num):
                            str_member = '\n'.join(divided_reaction_member[i])
                            embed.add_field(
                                name=f'group:{i}', value=f'{str_member}', inline=True)
                        embed.set_footer(text='よろしくお願いします')

                        await msg.edit(embed=embed)
                        await msg.clear_reactions()

                        break
                    else:
                        await msg.remove_reaction(str(reaction.emoji), user)

                elif str(reaction) == emoji_in:
                    if user.id in reaction_member:
                        pass
                    else:
                        reaction_member.append(user.mention)

    @shuffle.error
    async def shuffle_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'このコマンドを実行する権限がありません:{ctx.author.mention}')
        else:
            await ctx.send(f'to <@{self.bot.admin_id}> at {ctx.command.name} command\n{error}')


def setup(bot):
    bot.add_cog(CritiqueCog(bot))
