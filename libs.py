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
        except FileNotFoundError:
            pass
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
        dictionary = pd.read_csv(
            currentpath + "/data/scps.csv", index_col=0
        )
    except FileNotFoundError:
        pass

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
