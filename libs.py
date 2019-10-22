# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import os
import re

import pandas as pd
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
            return country[0] + "支部はまだは存在しませんよ？"
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
