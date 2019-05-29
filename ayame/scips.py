#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd
import requests

target_url = {"jp1": "http://ja.scp-wiki.net/scp-series-jp",
              "jp2": "http://ja.scp-wiki.net/scp-series-jp-2",
              "en1": "http://ja.scp-wiki.net/scp-series",
              "en2": "http://ja.scp-wiki.net/scp-series-2",
              "en3": "http://ja.scp-wiki.net/scp-series-3",
              "en4": "http://ja.scp-wiki.net/scp-series-4",
              "en5": "http://ja.scp-wiki.net/scp-series-5",
              "ru1": "http://ja.scp-wiki.net/scp-series-ru",
              "ko1": "http://ja.scp-wiki.net/scp-series-ko",
              "es1": "http://ja.scp-wiki.net/scp-series-es",
              "cn1": "http://ja.scp-wiki.net/scp-series-cn",
              "fr1": "http://ja.scp-wiki.net/scp-series-fr",
              "pl1": "http://ja.scp-wiki.net/scp-series-pl",
              "th1": "http://ja.scp-wiki.net/scp-series-th",
              "de1": "http://ja.scp-wiki.net/scp-series-de",
              "it1": "http://ja.scp-wiki.net/scp-series-it",
              "ua1": "http://ja.scp-wiki.net/scp-series-ua",
              "pt1": "http://ja.scp-wiki.net/scp-series-pt",
              "ex1": "http://ja.scp-wiki.net/scp-ex",
              }

start_word = {"jp": '<h1 id="toc1"><span>SCP-JP一覧 <a name="list"></a></span></h1>',
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
              "ex": '<h1 id="toc0"><span>SCP-EXシリーズ</span></h1>',
              }

end_word = {"jp": '<li><a href="/joke-scps-jp">Joke SCP-JP</a>',
            "en": '<li><a href="/joke-scps">Joke SCPs</a>',
            "ru": '<li><a href="/joke-scps-ru">Joke SCP-RU</a>',
            "ko": '<li><a href="/joke-scps-ko">Joke SCP-KO</a>',
            "es": '<li><a href="/joke-scps-es">Joke SCP-ES</a>',
            "cn": '<li><a href="/joke-scps-cn">Joke SCP-CN</a>',
            "fr": '<li><a href="/joke-scps-fr">Joke SCP-FR</a>',
            "pl": '<li><a href="/joke-scps-pl">Joke SCP-PL</a>',
            "th": '<li><a href="/joke-scps-th">Joke SCP-TH</a>',
            "de": '<li><a href="/joke-scps-de">Joke SCP-DE</a>',
            "it": '<li><a href="/joke-scps-it">Joke SCP-IT</a>',
            "ua": '<li><a class="newpage" href="/joke-scps-ua">Joke SCP-UA</a>',
            "pt": '<li><a href="/joke-scps-pt">Joke SCP-PT</a>',
            "ex": '</ul>',
            }


keys = ["jp1", "jp2", "en1", "en2", "en3", "en4", "en5", "ru1",
        "ko1", "cn1", "fr1", "pl1", "th1", "de1", "it1", "ua1",
        "pt1", "es1", "ex1"]


def scips():
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
    df.to_csv(masterpath + "/data/scps.csv", header=False, encoding="utf-8")


if __name__ == "__main__":
    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scips()

    print("報告書データベースの更新、完了しました。")
