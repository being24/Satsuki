#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd
import requests

target_url = ["http://ja.scp-wiki.net/scp-001-jp",
              "http://ja.scp-wiki.net/scp-001",
              ]


def proposal():
    """for scpjp-proposal"""

    urls = []
    titles = []
    brts = []

    for url in target_url:
        if "jp" in url:
            brt = "jp"
        else:
            brt = "en"

        response = requests.get(url)
        if response.status_code is not requests.codes.ok:
            print("request err")
            return 1

        scp_lines = response.text.split("\n")

        scp_start = scp_lines.index(
            '<p><em>ようこそ、担当職員様。ご希望のファイルを選択してください。</em></p>')
        for line in scp_lines[scp_start+5:]:
            if line == "</div>":
                break
            if "http://ja.scp-wiki.net" in line:
                line = line.replace("http://ja.scp-wiki.net", "")

            if "<p>" in line:
                url = re.search("<a.*?href=.*?>", line)
                url = re.split('("/.*?")', url.group())
                urls.append(url[1].replace('"', ''))

                title = ""
                for sptitle in re.split("<.*?>", line)[2:]:
                    title = title + sptitle
                title = title.replace("&quot;", '"').replace(
                    "&#8230;", "…").replace("&amp;", "&").replace("&#160;", " ").replace("&#8212;", "-")
                title = title.replace("''", '"')
                titles.append(title)
            brts.append(brt)

    df = pd.DataFrame(urls, titles)
    df[""] = brts

    df.to_csv(masterpath + "/data/proposal.csv",
              header=False, encoding="utf-8")


if __name__ == "__main__":
    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proposal()

    print("提言データベースの更新、完了しました。")
