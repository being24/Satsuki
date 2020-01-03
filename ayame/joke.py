#!/usr/bin/env python
# coding: utf-8

import html
import os
import re

import pandas as pd
import requests

target_url = {"en": "http://ja.scp-wiki.net/joke-scps",
              "jp": "http://ja.scp-wiki.net/joke-scps-jp",
              "ru": "http://ja.scp-wiki.net/joke-scps-ru",
              "ko": "http://ja.scp-wiki.net/joke-scps-ko",
              "cn": "http://ja.scp-wiki.net/joke-scps-cn",
              "fr": "http://ja.scp-wiki.net/joke-scps-fr",
              "pl": "http://ja.scp-wiki.net/joke-scps-pl",
              "es": "http://ja.scp-wiki.net/joke-scps-es",
              "th": "http://ja.scp-wiki.net/joke-scps-th",
              "de": "http://ja.scp-wiki.net/joke-scps-de",
              "it": "http://ja.scp-wiki.net/joke-scps-it",
              "ua": "http://ja.scp-wiki.net/joke-scps-ua",
              "pt": "http://ja.scp-wiki.net/joke-scps-pt",
              "uo": "http://ja.scp-wiki.net/joke-scp-series-unofficial"
              }

start_word = {"en": '<div class="content-panel standalone series">',
              "jp": '<div class="content-panel standalone series">',
              "ru": '<div class="content-panel standalone series">',
              "ko": '<div class="content-panel standalone series">',
              "cn": '<div class="content-panel standalone series">',
              "fr": '<div class="content-panel standalone series">',
              "pl": '<div class="content-panel standalone series">',
              "es": '<div class="content-panel standalone series">',
              "th": '<div class="content-panel standalone series">',
              "de": '<div class="content-panel standalone series">',
              "it": '<div class="content-panel standalone series">',
              "ua": '<div class="content-panel standalone series">',
              "pt": '<div class="content-panel standalone series">',
              "uo": '<div class="content-panel standalone series">',
              }

end_word = {"en": '</div>',
            "jp": '</div>',
            "ru": '</div>',
            "ko": '</div>',
            "cn": '</div>',
            "fr": '</div>',
            "pl": '</div>',
            "es": '</div>',
            "th": '</div>',
            "de": '</div>',
            "it": '</div>',
            "ua": '</div>',
            "pt": '</div>',
            "uo": '</div>',
            }


def joke():

    nums = []
    titles = []
    brts = []

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for key in target_url.keys():
        response = requests.get(target_url[key])
        if response.status_code is not requests.codes.ok:
            print(f"\t{key} request err : {response.status_code}")
            continue

        number = ""

        scp_lines = response.text.split("\n")

        scp_start = scp_lines.index(start_word[key])

        for line in scp_lines[scp_start:]:
            if end_word[key] in line:
                break
            if "<li>" in line:
                line = html.unescape(line)

                if "a href=" in line:
                    line = line.replace("http://ja.scp-wiki.net", "")
                    number = re.search("<a.*?href=.*?>", line)
                # print(number.group())  # debug
                    try:
                        number = re.split('("/.*?")', number.group())
                    except BaseException:
                        print("warn")
                        return

                    number = number[1].replace('"', "")
                    nums.append(number)
                    metatitle = ""
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

                    metatitle = metatitle.replace("''", '"')

                    titles.append(metatitle)
                    brts.append(key)

        print(f"\tpage:{key}のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    df['url'] = nums
    df['title'] = titles
    df['branches'] = brts

    df.to_csv(masterpath + "/data/joke.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:jokeデータベースの更新を開始します。")

    joke()

    print("菖蒲:jokeデータベースの更新、完了しました。")
