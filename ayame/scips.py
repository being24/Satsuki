#!/usr/bin/env python
# coding: utf-8

import html
import os
import re


import pandas as pd
import requests

target_url = {"jp0": "http://ja.scp-wiki.net/scp-series-jp",
              "jp1": "http://ja.scp-wiki.net/scp-series-jp-2",
              "jp2": "http://ja.scp-wiki.net/scp-series-jp-3",
              "en0": "http://ja.scp-wiki.net/scp-series",
              "en1": "http://ja.scp-wiki.net/scp-series-2",
              "en2": "http://ja.scp-wiki.net/scp-series-3",
              "en3": "http://ja.scp-wiki.net/scp-series-4",
              "en4": "http://ja.scp-wiki.net/scp-series-5",
              "en5": "http://ja.scp-wiki.net/scp-series-6",
              "ru1": "http://ja.scp-wiki.net/scp-list-ru",
              "ko0": "http://ja.scp-wiki.net/scp-series-ko",
              "es0": "http://ja.scp-wiki.net/serie-scp-es",
              "cn0": "http://ja.scp-wiki.net/scp-series-cn",
              "cn1": "http://ja.scp-wiki.net/scp-series-cn-2",
              "fr0": "http://ja.scp-wiki.net/liste-francaise",
              "pl0": "http://ja.scp-wiki.net/lista-pl",
              "th0": "http://ja.scp-wiki.net/scp-series-th",
              "de0": "http://ja.scp-wiki.net/scp-de",
              "it0": "http://ja.scp-wiki.net/scp-it-serie-i",
              "ua0": "http://ja.scp-wiki.net/scp-series-ua",
              "pt0": "http://ja.scp-wiki.net/series-1-pt",
              "cs0": "http://ja.scp-wiki.net/scp-series-cs",
              "uo0": "http://ja.scp-wiki.net/scp-series-unofficial"
              }

start_word = {
    "jp": '<h1 id="toc1"><span>SCP-JP一覧 <a name="list"></a></span></h1>',
    "en": '<h1 id="toc1"><span>SCP一覧 <a name="list"></a></span></h1>',
    "ru": '<h1 id="toc1"><span>SCP-RU一覧 <a name="list"></a></span></h1>',
    "ko": '<h1 id="toc1"><span>SCP-KO一覧 <a name="list"></a></span></h1>',
    "es": '<h1 id="toc1"><span>SCP-ES一覧 <a name="list"></a></span></h1>',
    "cn": '<h1 id="toc1"><span>SCP-CN一覧 <a name="list"></a></span></h1>',
    "fr": '<h1 id="toc1"><span>SCP-FR一覧 <a name="list"></a></span></h1>',
    "pl": '<h1 id="toc1"><span>SCP-PL一覧 <a name="list"></a></span></h1>',
    "th": '<h1 id="toc1"><span>SCP-TH一覧 <a name="list"></a></span></h1>',
    "de": '<h1 id="toc1"><span>SCP-DE一覧 <a name="list"></a></span></h1>',
    "it": '<h1 id="toc1"><span>SCP-IT一覧 <a name="list"></a></span></h1>',
    "ua": '<h1 id="toc1"><span>SCP-UA一覧 <a name="list"></a></span></h1>',
    "pt": '<h1 id="toc1"><span>SCP-PT一覧 <a name="list"></a></span></h1>',
    "cs": '<h1 id="toc1"><span>SCP-CS一覧 <a name="list"></a></span></h1>',
    "uo": '<h1 id="toc1"><span>SCP一覧 <a name="list"></a></span></h1>'}

end_word = {
    "jp": '<li><a href="/joke-scps-jp">Joke SCP-JP</a>',
    "en": '<li><a href="/joke-scps">Joke SCPs</a>',
    "ru": '<li><a href="/joke-scps-ru">Joke SCP-RU</a>',
    "ko": '<li><a href="/joke-scps-ko">Joke SCP-KO</a>',
    "es": '<li><a href="/joke-scps-es">Joke SCP-ES</a>',
    "cn": '<li><a href="/joke-scps-cn">Joke SCP-CN</a>',
    "fr": '<li><a href="/joke-scps-fr">Joke SCP-FR</a>',
    "pl": '<li><a href="/joke-scps-pl">Joke SCP-PL</a>',
    "th": '<li><a href="/joke-scps-th">Joke SCP-TH</a>',
    "de": '<li><a href="/joke-scps-de">Joke SCP-DE</a>',
    "it": '<li><a class="newpage" href="/joke-scps-it">Joke SCP-IT</a>',
    "ua": '<li><a class="newpage" href="/joke-scps-ua">Joke SCP-UA</a>',
    "pt": '<li><a href="/joke-scps-pt">Joke SCP-PT</a>',
    "cs": '</div>',
    "uo": '<li><a href="/joke-scp-series-unofficial">Joke SCP</a>'}


def scips():
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

        res_key = key[:-1]
        scp_start = scp_lines.index(start_word[res_key])

        for line in scp_lines[scp_start:]:
            if end_word[res_key] in line:
                break
            if "<li>" in line:
                line = html.unescape(line)
                if "newpage" in line:
                    continue
                if "href=" in line:
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

                    if number == "/scp-4494":
                        metatitle = "The Specter、正義の戦士！"  # 敗北感
                    elif number == "/scp-1355-jp":  # 一文字づつ精査→*を\*にするのもありっちゃあり
                        metatitle = r"SCP-1355-JP - /\*Kingdom\*/"
                    titles.append(metatitle)

                    brts.append(res_key)

        print(f"\tpage:{key}のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    df['url'] = nums
    df['title'] = titles
    df['branches'] = brts
    df.to_csv(masterpath + "/data/scps.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:報告書データベースの更新を開始します。")
    scips()
    print("菖蒲:報告書データベースの更新、完了しました。")
