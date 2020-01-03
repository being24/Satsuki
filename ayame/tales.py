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


def tale():
    urls = []
    titles = []
    authors = []
    brts = []

    author = ""
    title = ""
    url = ""

    masterpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for key in target_url.keys():
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

            # author start
            elif '<th style="font-size:125%"' in line:
                author = re.search('alt=".*?"', line)
                if author is not None:
                    author = author.group()[5:-1]

                if author is None:
                    author = re.search("<strong>.*?</strong>", line)
                    if author is not None:
                        author = author.group()[8:-9]

                if author is None:
                    author = re.search("<em>.*?</em>", line)
                    if author is not None:
                        author = author.group()[4:-5]

                if author is None:
                    author = "Unknown pattern of author"

            elif '<p><strong>' in line:
                author = line.replace("<p><strong>", "")
                author = author.replace("</strong></p>", "")

            elif '<p><span class="printuser">' in line:
                author = line[line.find(
                    'return false;">') + len('return false;">'):]
                author = author.replace("</a></span></p>", "")

            elif '<p><span class="error-inline">' in line:
                author = line[line.find('<p><span class="error-inline"><em>') +
                              len('<p><span class="error-inline"><em>'): -
                              len('</em> does not match any existing user name</span></p>')]
            # author end

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

                urls.append(url)
                titles.append(title)
                authors.append(author)
                brts.append(key)

        print(f"page:{key}のデータ取得が完了しました。")

    df = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    df['url'] = urls
    df['title'] = titles
    df['author'] = authors
    df['branches'] = brts
    df.to_csv(masterpath + "/data/tale.csv", header=True, encoding="utf-8")


if __name__ == "__main__":
    print("菖蒲:taleデータベースの更新を更新します。")
    tale()
    print("菖蒲:taleデータベースの更新、完了しました。")
