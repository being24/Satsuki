# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import html
import itertools
import os
import re

import feedparser
import pandas as pd
import requests
import zenhan

BRANCHS = ['jp', 'en', 'ru', 'ko', 'es', 'cn',
           'fr', 'pl', 'th', 'de', 'it', 'ua', 'pt', 'uo']
currentpath = os.path.dirname(os.path.abspath(__file__))


def get_country_from_code(brt):
    if brt.isalpha():
        brt = brt.upper()
        try:
            dictionary = pd.read_csv(
                currentpath + "/data/ISO3166-1.CSV"
            )
        except FileNotFoundError as e:
            print(e)
        country = dictionary.query('二字 == @brt')
        if country.empty:
            return "該当する国コードは存在しません"
        else:
            country = country.values.tolist()
            country = itertools.chain(*country)
            country = list(country)
            return country[0] + "支部はまだ存在しませんよ？"
    else:
        return "国コードが正しくありません."


def scp_number(msg):
    msg = zenhan.z2h(msg.casefold()).replace("-", "").replace("scp", "")
    number = re.sub("\\D", "", msg)

    if number is (None and ""):
        return None

    brt = msg.replace(number, "")

    if brt is "":
        brt = "en"

    if brt not in BRANCHS:  # 要改良
        reply = get_country_from_code(brt)
        return reply

    try:
        dictionary = pd.read_csv(currentpath + "/data/scps.csv", index_col=0)
    except FileNotFoundError as e:
        print(e)

    result = dictionary.query('branches in @brt')
    result = result.query('url.str.contains(@number)', engine='python')
    result = result[0:1].values.tolist()
    result = itertools.chain(*result)
    result = list(result)

    if len(result) == 0 or number is re.sub("\\D", "", result[0]):
        if len(number) > 4:
            return None
        if "en" in brt:
            return("scp-" + str(number) + "はまだ存在しません")
        else:
            return("scp-" + str(number) + "-" + str(brt) + "はまだ存在しません")

    return(result)


def src_tale(msg):
    result = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/tale.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    '''if brt is not "*":
        dictionary = dictionary.query('branches in @brt')'''

    dictionary_url = dictionary.query(
        'url.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    dictionary_author = dictionary.query(
        'author.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_url, dictionary_title, dictionary_author])
    result = result.drop_duplicates()

    return result


def src_proposal(msg):
    result = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/proposal.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_url = dictionary.query(
        'url.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_url, dictionary_title])
    result = result.drop_duplicates()

    return result


def src_joke(msg):
    result = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/joke.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_url = dictionary.query(
        'url.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_url, dictionary_title])
    result = result.drop_duplicates()

    return result


def src_guide(msg):
    result = pd.DataFrame(columns=['url', 'title', 'description'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/guide_hub.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_url = dictionary.query(
        'url.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_url, dictionary_title])
    result = result.drop_duplicates()

    return result


def src_author(msg):
    result = pd.DataFrame(
        columns=[
            'url',
            'title',
            'author',
            'branches',
            'image'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/author.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_author = dictionary.query(
        'author.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_author, dictionary_title])
    result = result.drop_duplicates()

    return result


def src_explained(msg):
    result = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/exs.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_url = dictionary.query(
        'url.str.contains(@msg)', engine='python')

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_url, dictionary_title])
    result = result.drop_duplicates()

    return result


def src_scp(msg):
    result = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])

    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/scps.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    dictionary_title = dictionary.query(
        'title.str.contains(@msg)', engine='python')

    result = pd.concat([dictionary_title])
    result = result.drop_duplicates()

    return result


def get_scp_rss(target):
    feed_data = feedparser.parse(target)
    scp_rss = []
    for entries in feed_data['entries']:
        title = (entries['title'])
        link = (entries['link'])
        text = entries["content"][0]['value']
        scp_rss.append([link, title, text])
    return scp_rss


def tag_to_discord(content):
    result = []
    for line in content:
        line = line.replace("<p>", "\n")
        line = line.replace("</p>", "\n")
        line = line.replace("</div>", "")

        line = line.replace("<br />", "\n")

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

        if 'href' in line:
            match = re.findall(r'href=[\'"]?([^\'" >]+)', line)
            if len(match) == 0:
                line = ""
            elif "javascript" in match[0]:
                line = ""

            if len(match) != 0:
                deco_f = f'['
                deco_b = f"]({match[0]})"

            p = re.compile(r"<[^>]*?>")
            line = p.sub(f"{deco_b}", line)
            line = line.replace(deco_b, deco_f, 1)

        line = html.unescape(line)
        result.append(line)

    return result


def statistics_csv():
    dictionary = pd.DataFrame(columns=['url', 'title', 'author', 'branches'])
    try:
        dictionary = pd.read_csv(
            currentpath +
            f"/data/scps.csv",
            index_col=0)
    except FileNotFoundError as e:
        print(e)

    num_dict = {}

    num_dict["all"] = len(dictionary)

    for brt in BRANCHS:
        num_dict[brt] = len(dictionary.query('branches in @brt'))

    return num_dict
