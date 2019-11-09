#!/usr/bin/env python
# coding: utf-8

import html
import os
import re

import pandas as pd
import requests
from prettyprinter import cpprint

target_url = "http://ja.scp-wiki.net/guide-hub"
start_word = '<h1 id="toc0"><span>先ずはこれを読んでください</span></h1>'
end_word = '<div class="footnotes-footer">'


def guide_hub():
    response = requests.get(target_url)
    if response.status_code is not requests.codes.ok:
        print(f"request err : {response.status_code}")

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    lines = response.text.split("\n")
    start = lines.index(start_word)

    df = pd.DataFrame(columns=['url', 'title', 'description'])

    urls = []
    titles = []
    descriptions = []

    for line in lines[start:]:

        line = html.unescape(line)

        if end_word in line:
            break

        if 'href' in line:
            sp_line = re.split(r'[<>]', line)
            # 要改善
            for i, sp in enumerate(sp_line):
                if 'href' in sp:
                    if 'newpage' in sp_line[i]:
                        url = sp_line[i].replace(
                            'a class="newpage" href=', "").replace(
                            '"', "")
                    else:
                        url = sp_line[i].replace(
                            'a href=', "").replace(
                            '"', "")
                    urls.append(url)
                    titles.append(sp_line[i + 1])
                    descriptions.append(sp_line[i + 5].replace(": ", ''))
                    break

    df['url'] = urls
    df['title'] = titles
    df['description'] = descriptions

    df.to_csv(masterpath + "/data/guide_hub.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:ガイドハブデータベースの更新を開始します。")

    guide_hub()

    print("菖蒲:ガイドハブデータベースの更新、完了しました。")
