#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd
import requests

target_url = {"tales-jp": "http://ja.scp-wiki.net/foundation-tales-jp",
              "tales-en": "http://ja.scp-wiki.net/foundation-tales",
              }

start_word = {"tales-jp": '<p>アルファベット順著者</p>',
              "tales-en": '<p>アルファベット順著者</p>',
              }

end_word = {"tales-jp": '<td>その他<a name="misc"></a></td>',
            "tales-en": '<td>その他<a name="misc"></a></td>',
            }

keys = ["tales-jp", "tales-en"]


def tales():
    urls = []
    titles = []
    authers = []
    auther = ""
    title = ""
    url = ""

    for key in keys:
        response = requests.get(target_url[key])
        if response.status_code is not requests.codes.ok:
            print("request err")
            return 1

        scp_lines = response.text.split("\n")
        tales_start = scp_lines.index(start_word[key])

        for line in scp_lines:
            if re.match('<td>\s</td>', line):
                scp_lines.remove(line)
            elif re.match('<td>.<a name="."></a></td>', line):
                scp_lines.remove(line)
            elif '⇑' in line:
                scp_lines.remove(line)

        for line in scp_lines[tales_start:]:
            if end_word[key] in line:
                break

            elif '<th style="font-size:125%"' in line:
                auther = re.search('alt=".*?"', line)
                if auther is not None:
                    auther = auther.group()[5:-1]

                if auther is None:
                    auther = re.search("<strong>.*?</strong>", line)
                    if auther is not None:
                        auther = auther.group()[8:-9]
                if auther is None:
                    auther = re.search("<em>.*?</em>", line)
                    if auther is not None:
                        auther = auther.group()[4:-5]

                if auther is None:
                    auther = "Unknown pattern of auther"

            elif '<td><a href="#top">' in line:
                pass

            elif 'http://ja.scp-wiki.net/forum/t-6047066/' in line:
                pass

            elif '<td><a href="/scp' in line:
                pass

            elif '<td><a href="/1600con17"' in line:
                pass

            elif '<td><a href="/warucontest">' in line:
                pass

            elif '<td><a href="/author:' in line:
                pass

            elif '<td><a href="/venture-contest-2018' in line:
                pass

            elif '<td><a href="/lily-s-proposal">' in line:
                pass

            elif '<td><a href="/newface-contest-hub' in line:
                pass

            elif '<td><a href="/personnel-the-origin-hub' in line:
                pass

            elif "<td><a href=" in line:
                line = line.replace("&quot;", '"').replace(
                    "&#8230;", "…").replace("&amp;", "&")
                line = line.replace("''", '"')

                sp_line = re.split('[<>]', line)
                url = sp_line[3].replace('"', "").replace("a href=", "")
                title = sp_line[4]
                urls.append(url)
                titles.append(title)
                authers.append(auther)

            elif '<td><a target="_blank" href="' in line:
                sp_line = re.split('[<>]', line)
                url = sp_line[3].replace('"', "").replace(
                    'a target=_blank href=http://ja.scp-wiki.net', "")
                title = sp_line[4]
                urls.append(url)
                titles.append(title)
                authers.append(auther)

        print("page:" + key + "のデータ取得が完了しました。")

    df = pd.DataFrame(urls, titles)
    df[''] = authers

    df.to_csv(masterpath + "/data/tale.csv", header=False, encoding="utf-8")


if __name__ == "__main__":
    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tales()

    print("菖蒲:taleデータベースの更新、完了しました。")
