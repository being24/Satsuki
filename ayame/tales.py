#!/usr/bin/env python
# coding: utf-8

import html
import os
import re

import pandas as pd
import requests

target_url = {"jp": "http://ja.scp-wiki.net/foundation-tales-jp",
              "en": "http://ja.scp-wiki.net/foundation-tales",
              "ru": "http://ja.scp-wiki.net/foundation-tales-ru",
              "cn": "http://ja.scp-wiki.net/foundation-tales-cn",
              "fr": "http://ja.scp-wiki.net/foundation-tales-fr",
              "pl": 'http://ja.scp-wiki.net/foundation-tales-pl',
              "es": 'http://ja.scp-wiki.net/foundation-tales-es',
              "de": 'http://ja.scp-wiki.net/foundation-tales-de',
              "th": 'http://ja.scp-wiki.net/foundation-tales-th',
              "it": 'http://ja.scp-wiki.net/foundation-tales-it',
              "ua": 'http://ja.scp-wiki.net/foundation-tales-ua',
              "pt": 'http://ja.scp-wiki.net/foundation-tales-pt',
              "ko": 'http://ja.scp-wiki.net/foundation-tales-ko'
              }

start_word = {"jp": '<p>アルファベット順著者</p>',
              "en": '<p>アルファベット順著者</p>',
              "ru": '<h1 id="toc0"><span>著作者順</span></h1>',
              "cn": '<h1 id="toc0"><span>著作者順</span></h1>',
              "fr": '<h1 id="toc1"><span>著作者順</span></h1>',
              "pl": '<h1 id="toc0"><span>著作者順</span></h1>',
              "es": '<h1 id="toc0"><span>著作者順</span></h1>',
              "de": '<h1 id="toc0"><span>著作者順</span></h1>',
              "th": '<h1 id="toc0"><span>著作者順</span></h1>',
              "it": '<h1 id="toc0"><span>著作者順</span></h1>',
              "ua": '<h1 id="toc0"><span>著作者順</span></h1>',
              "pt": '<h1 id="toc0"><span>著作者順</span></h1>',
              "ko": '<h1 id="toc0"><span>著作者順</span></h1>',
              }

end_word = {"jp": '<td>その他<a name="misc"></a></td>',
            "en": '<td>その他<a name="misc"></a></td>',
            "ru": '</div>',
            "cn": '</div>',
            "fr": '</div>',
            "pl": '</div>',
            "es": '</div>',
            "de": '</div>',
            "th": '</div>',
            "it": '</div>',
            "ua": '</div>',
            "pt": '</div>',
            "ko": '</div>',
            }

keys = [
    "jp",
    "en",
    "ru",
    "cn",
    "fr",
    "pl",
    "es",
    "de",
    "th",
    "it",
    "ua",
    "pt",
    "ko"]


exclusion_list = ['#top',
                  'http://ja.scp-wiki.net/forum/t-6047066/',
                  # '<td><a href="/scp',
                  '<td><a href="/1600con17"',
                  '<td><a href="/warucontest">',
                  '<td><a href="/author:',
                  '<td><a href="/venture-contest-2018',
                  '<td><a href="/lily-s-proposal">',
                  '<td><a href="/newface-contest-hub',
                  '<td><a href="/personnel-the-origin-hub',
                  ]


def tales():
    urls = []
    titles = []
    authers = []
    brts = []

    auther = ""
    title = ""
    url = ""

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for key in keys:
        response = requests.get(target_url[key])
        if response.status_code is not requests.codes.ok:
            print(f"{key} request err : {response.status_code}")
            continue

        scp_lines = response.text.split("\n")
        tales_start = scp_lines.index(start_word[key])

        for line in scp_lines:
            if re.match(r'<td>\s</td>', line):
                scp_lines.remove(line)
            elif re.match('<td>.<a name="."></a></td>', line):
                scp_lines.remove(line)
            elif '⇑' in line:
                scp_lines.remove(line)

        for line in scp_lines[tales_start:]:
            line = html.unescape(line)

            if end_word[key] in line:
                break

            # auther start
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

            elif '<p><strong>' in line:
                auther = line.replace("<p><strong>", "")
                auther = auther.replace("</strong></p>", "")

            elif '<p><span class="printuser">' in line:
                auther = line[line.find(
                    'return false;">') + len('return false;">'):]
                auther = auther.replace("</a></span></p>", "")

            elif '<p><span class="error-inline">' in line:
                auther = line[line.find('<p><span class="error-inline"><em>') +
                              len('<p><span class="error-inline"><em>'): -
                              len('</em> does not match any existing user name</span></p>')]
            # auther end

            # url,title start
            elif any([s for s in exclusion_list if s in line]):
                pass

            else:
                if "<td><a href=" in line:
                    sp_line = re.split('[<>]', line)
                    url = sp_line[3].replace('"', "").replace("a href=", "")
                    title = sp_line[4]

                elif '<td><a target="_blank" href="' in line:
                    sp_line = re.split('[<>]', line)
                    url = sp_line[3].replace('"', "").replace(
                        'a target=_blank href=http://ja.scp-wiki.net', "")
                    title = sp_line[4]

                elif '<li><a href="' in line:
                    sp_line = re.split('[<>]', line)
                    url = sp_line[3].replace('"', "").replace("a href=", "")
                    title = sp_line[4]

                else:
                    continue

                if 'http://ja.scp-wiki.net/' in url:
                    url = url.replace("http://ja.scp-wiki.net", '')

                
            # url,title end

                urls.append(url)
                titles.append(title)
                authers.append(auther)
                brts.append(key)

        print("page:" + key + "のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'auther', 'branches'])

    df['url'] = urls
    df['title'] = titles
    df['auther'] = authers
    df['branches'] = brts

    df.to_csv(masterpath + "/data/tale.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:taleデータベースの更新を更新します。")
    tales()

    print("菖蒲:taleデータベースの更新、完了しました。")
