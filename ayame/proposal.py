#!/usr/bin/env python
# coding: utf-8

import html
import os
import re

import pandas as pd
import requests

target_url = {'jp': "http://ja.scp-wiki.net/scp-001-jp",
              'en': "http://ja.scp-wiki.net/scp-001",
              'ko': 'http://ja.scp-wiki.net/scp-001-ko',
              'cn': 'http://ja.scp-wiki.net/scp-001-cn',
              'fr': 'http://ja.scp-wiki.net/scp-001-fr',
              'pl': 'http://ja.scp-wiki.net/scp-001-pl',
              'es': 'http://ja.scp-wiki.net/scp-es-001',
              'th': 'http://ja.scp-wiki.net/scp-001-th',
              'de': 'http://ja.scp-wiki.net/scp-001-de',
              'it': 'http://ja.scp-wiki.net/scp-001-it',
              'ua': 'http://ja.scp-wiki.net/scp-001-ua',
              'pt': 'http://ja.scp-wiki.net/scp-001-pt',
              'cs': 'http://ja.scp-wiki.net/scp-001-cs',
              'ru': 'http://ja.scp-wiki.net/scp-1001-ru'
              }


def proposal():
    urls = []
    titles = []
    brts = []

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for brt in target_url.keys():
        response = requests.get(target_url[brt])
        if response.status_code is not requests.codes.ok:
            print(f"\t{brt} request err : {response.status_code}")
            continue

        scp_lines = response.text.split("\n")

        if '<p><em>ようこそ、担当職員様。ご希望のファイルを選択してください。</em></p>' in scp_lines:  # ここ変えたい
            scp_start = scp_lines.index(
                '<p><em>ようこそ、担当職員様。ご希望のファイルを選択してください。</em></p>')
        elif '<p style="text-align: center;"><em>ようこそ、担当職員様。ご希望のファイルを選択してください。</em></p>' in scp_lines:
            scp_start = scp_lines.index(
                '<p style="text-align: center;"><em>ようこそ、担当職員様。ご希望のファイルを選択してください。</em></p>')
            scp_start = scp_start - 3

        for line in scp_lines[scp_start + 5:]:
            line = html.unescape(line)

            if line == "</div>":
                break
            if "http://ja.scp-wiki.net" in line:
                line = line.replace("http://ja.scp-wiki.net", "")

            if "<p>" in line:
                try:
                    url = re.search("<a.*?href=.*?>", line)
                    url = re.split('("/.*?")', url.group())
                    urls.append(url[1].replace('"', ''))
                    brts.append(brt)

                except AttributeError:
                    continue

                title = ""
                for sptitle in re.split("<.*?>", line)[2:]:
                    title = title + sptitle

                title = title.replace("''", '"')
                titles.append(title)

        print(f"\tpage:{brt}のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    df['url'] = urls
    df['title'] = titles
    df['branches'] = brts

    df.to_csv(masterpath + "/data/proposal.csv",
              header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:提言データベースの更新を開始します。")

    proposal()

    print("菖蒲:提言データベースの更新、完了しました。")
