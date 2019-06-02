# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config
import os
import sys
import traceback  # エラー表示のためにインポート

import discord
from discord.ext import commands

INITIAL_COGS = [
    'cogs.tachibana_cog'
]


class MyBot(commands.Bot):

    def __init__(self, command_prefix):  # コンストラクタ

        super().__init__(command_prefix)  # スーパークラスのコンストラクタに値を渡して実行。

        for cog in INITIAL_COGS:  # INITIAL_COGSに格納されている名前から、コグを読み込む。
            try:
                self.load_extension(cog)

            except Exception:  # エラーが発生した場合は、エラー内容を表示。
                traceback.print_exc()

    async def on_ready(self):  # 起動時実行されるコマンド
        print('-----')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        logging.info('rebooted')


def read_token():  # トークンを 'root/token.ini' から取得する
    file = currentpath + "/token.ini"
    try:
        for line in open(file, 'r'):
            temp = line.replace(" ", "").strip().split("=")
            token = temp[1]
    except FileNotFoundError:
        print("ファイルが見つかりません・・・。")
        print(sys.exc_info())

    return token


if __name__ == '__main__':

    currentpath = os.path.dirname(os.path.abspath(__file__))

    token = read_token()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.FileHandler(
        currentpath + "/data/log/logger.log", 'a', 'utf-8')
    formatter = logging.Formatter(
        '%(levelname)s : %(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # コマンドの最初の文字として'/'をcommand_prefixとする。
    bot = MyBot(command_prefix='/')
    bot.run(token)  # Botのトークン
