#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd
import requests


target_url = {"ej1": "http://ja.scp-wiki.net/joke-scps",
              "jj1": "http://ja.scp-wiki.net/joke-scps-jp",
              }

start_word = {"ej": '<div class="content-panel standalone series">',
              "jj": '<div class="content-panel standalone series">',
              }

end_word = {"ej": '</div>',
            "jj": '</div>',
            }

keys = ["jj1", "ej1"]


def joke():

    nums = []
    titles = []

    for key in keys:
        response = requests.get(target_url[key])
        if response.status_code is not requests.codes.ok:
            print("request err")
            return 1

        number = ""

        scp_lines = response.text.split("\n")

        res_key = key[:-1]
        scp_start = scp_lines.index(start_word[res_key])

        for line in scp_lines[scp_start:]:
            if end_word[res_key] in line:
                break
            if "<li>" in line:
                if "a href=" in line:
                    line = line.replace("http://ja.scp-wiki.net", "")
                    number = re.search("<a.*?href=.*?>", line)
                # print(number.group())  # debug
                    try:
                        number = re.split('("/.*?")', number.group())
                    except:
                        logging.warn("line = " + line)
                        logging.warn("Type conversion err", exc_info=True)
                        print("warn")
                        return

                    number = number[1].replace('"', "")
                    nums.append(number)
                    metatitle = ""
                    # http://ja.scp-wiki.net/scp-3349 あかん！あかん！
                    # この辺、バグ呼ぶだろうなあ・・・
                    if '<span style="font-size:0%;">' in line:  # siz0%
                        siz0_0 = line.find('<span style="font-size:0%;">')
                        siz0_1 = line.find(
                            '</span>', siz0_0 + 1) + len('</span>')
                        line = line.replace(
                            line[siz0_0:siz0_1], "")

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

                    for sptitle in re.split("<.*?>", line)[2:]:
                        metatitle = metatitle + sptitle
                    metatitle = metatitle.replace("&quot;", '"').replace(
                        "&#8230;", "…").replace("&amp;", "&").replace("&#160;", " ").replace("&#8212;", "-")
                    metatitle = metatitle.replace("''", '"')

                    if number == "/scp-4494":
                        metatitle = "The Specter、正義の戦士！"  # 敗北感
                    elif number == "/scp-1355-jp":  # 一文字づつ精査→*を\*にするのもありっちゃあり
                        metatitle = "SCP-1355-JP - /\*Kingdom\*/"
                    titles.append(metatitle)

        print("page:" + key + "のデータ取得が完了しました。")

    df = pd.DataFrame(titles, nums)
    df.to_csv(masterpath + "/data/joke.csv", header=False, encoding="utf-8")


if __name__ == "__main__":
    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    joke()

    print("jokeデータベースの更新、完了しました。")
