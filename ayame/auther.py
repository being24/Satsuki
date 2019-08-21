#!/usr/bin/env python
# coding: utf-8


import html
import os
import re

import pandas as pd
import requests
from prettyprinter import cpprint

target_url = "http://ja.scp-wiki.net/members-pages-jp"
start_word = '<h2 id="toc0"><span>管理者</span></h2>'
end_word = '<h2><span>著者ページへの参加条件</span></h2>'


def auther():
    response = requests.get(target_url)
    if response.status_code is not requests.codes.ok:
        print(f"{key} request err : {response.status_code}")

    lines = response.text.split("\n")
    start = lines.index(start_word)
    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    urls = []
    titles = []
    authers = []
    brts = []
    images = []

    for line in lines[start:]:
        auther = ""
        title = ""
        url = ""
        image = ""

        line = html.unescape(line)

        if end_word in line:
            break
        elif '<td><span class="printuser avatarhover">' in line:

            sp_line = re.split('[<>]', line)
            sp_line[7] = sp_line[7].replace(
                'img class="small" src="', "").split()[0]
            auther = sp_line[12].replace('"', "")
            image = sp_line[7].replace('"', "")
            authers.append(auther)
            images.append(image)

        elif '<td><span class="error-inline"><em>' in line:

            sp_line = re.split('[<>]', line)
            auther = sp_line[6]
            authers.append(auther)
            images.append(image)

        elif '<td><span' in line:

            sp_line = re.split('[<>]', line)
            url = sp_line[7].replace("a href=", "").replace('"', "")
            title = "~~" + sp_line[4] + "~~" + sp_line[8]
            urls.append(url)
            titles.append(title)
            brts.append("jp")

        elif '<td><a style' in line:

            sp_line = re.split('[<>]', line)
            url = sp_line[3][sp_line[3].find("/author"):].replace('"', '')

            del sp_line[:4]
            del sp_line[-4:]

            sp_line = [v for i, v in enumerate(sp_line) if i % 2 == 0]
            title = "".join(sp_line)
            urls.append(url)
            titles.append(title)
            brts.append("jp")

        elif '<td><a href="' in line:

            if 'http://ja.scp-wiki.net' in line:
                line = line.replace('http://ja.scp-wiki.net', "")
            sp_line = re.split('[<>]', line)
            url = sp_line[3].replace("a href=", "").replace('"', "")
            title = sp_line[4].replace('"', "")
            urls.append(url)
            titles.append(title)
            brts.append("jp")

        elif 'No memberPage' in line:

            sp_line = re.split('[<>]', line)
            title = sp_line[2]
            urls.append("")
            titles.append(title)
            brts.append("jp")

        else:
            continue

    df = pd.DataFrame(columns=['url', 'title', 'auther', 'branches', 'images'])

    df['url'] = urls
    df['title'] = titles
    df['auther'] = authers
    df['branches'] = brts
    df['images'] = images

    df.to_csv(masterpath + "/data/auther.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:著者ページデータベースの更新を開始します。")
    auther()

    print("菖蒲:著者ページデータベースの更新、完了しました。")
