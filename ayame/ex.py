#!/usr/bin/env python
# coding: utf-8

import html
import os
import re

import pandas as pd
import requests

target_url = {"en": "http://ja.scp-wiki.net/scp-ex",
              "jp": "http://ja.scp-wiki.net/scp-jp-ex",
              "ru": "http://ja.scp-wiki.net/scp-ru-ex",
              "ko": "http://ja.scp-wiki.net/scp-ko-ex",
              "cn": "http://ja.scp-wiki.net/scp-cn-ex",
              "fr": "http://ja.scp-wiki.net/scp-fr-ex",
              "pl": "http://ja.scp-wiki.net/scp-pl-ex",
              "es": "http://ja.scp-wiki.net/scp-es-ex",
              "th": "http://ja.scp-wiki.net/scp-th-ex",
              "de": "http://ja.scp-wiki.net/scp-de-ex",
              "it": "http://ja.scp-wiki.net/scp-it-ex",
              "ua": "http://ja.scp-wiki.net/scp-ua-ex",
              "pt": "http://ja.scp-wiki.net/scp-pt-ex",
              "uo": "http://ja.scp-wiki.net/explained-scp-series-unofficial"
              }

start_word = {"en": '<h1 id="toc0"><span>SCP-EXシリーズ</span></h1>',
              "jp": '<h1 id="toc0"><span>SCP-JP-EXシリーズ</span></h1>',
              "ru": '<h1 id="toc0"><span>SCP-RU-EXシリーズ</span></h1>',
              "ko": '<h1 id="toc0"><span>SCP-KO-EXシリーズ</span></h1>',
              "cn": '<h1 id="toc0"><span>SCP-CN-EXシリーズ</span></h1>',
              "fr": '<h1 id="toc0"><span>SCP-FR-EXシリーズ</span></h1>',
              "pl": '<h1 id="toc0"><span>SCP-PL-EXシリーズ</span></h1>',
              "es": '<h1 id="toc0"><span>SCP-ES-EXシリーズ</span></h1>',
              "th": '<h1 id="toc0"><span>SCP-TH-EXシリーズ</span></h1>',
              "de": '<h1 id="toc0"><span>SCP-DE-EXシリーズ</span></h1>',
              "it": '<h1 id="toc0"><span>SCP-IT-EXシリーズ</span></h1>',
              "ua": '<h1 id="toc0"><span>SCP-UA-EXシリーズ</span></h1>',
              "pt": '<h1 id="toc0"><span>SCP-PT-EXシリーズ</span></h1>',
              }

end_word = {"en": '</ul>',
            "jp": '</ul>',
            "ru": '</ul>',
            "ko": '</ul>',
            "cn": '</ul>',
            "fr": '</ul>',
            "pl": '</ul>',
            "es": '</ul>',
            "th": '</ul>',
            "de": '</ul>',
            "it": '</ul>',
            "ua": '</ul>',
            "pt": '</ul>',
            }


keys = [
    "en",
    "jp",
    "ru",
    "ko",
    "cn",
    "fr",
    "pl",
    "es",
    "th",
    "de",
    "it",
    "ua",
    "pt"]


def ex():
    nums = []
    titles = []
    brts = []

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for key in keys:
        response = requests.get(target_url[key])
        if response.status_code is not requests.codes.ok:
            print(f"{key} request err : {response.status_code}")
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

                    metatitle = metatitle.replace("''", '"')

                    titles.append(metatitle)

                    brts.append(key)

        print("page:" + key + "のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    df['url'] = nums
    df['title'] = titles
    df['branches'] = brts
    df.to_csv(masterpath + "/data/exs.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:解明済み事象のデータベースの更新を開始します。")

    ex()

    print("菖蒲:解明済み事象のデータベースの更新、完了しました。")
