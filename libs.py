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


def scp_number(self, msg):
    msg = zenhan.z2h(msg.casefold()).replace("-", "").replace("scp", "")
    number = re.sub("\\D", "", msg)

    if number is (None and ""):
        return None

    brt = msg.replace(number, "")

    if brt is "":
        brt = "en"

    if brt not in BRANCHS:  # 要改良
        reply = brt + "支部は存在しませんよ？"
        return reply

    try:
        dictionary = pd.read_csv(
            currentpath + "/data/scps.csv", index_col=0
        )
    except FileNotFoundError:
        pass

    result = dictionary.query('branches in @brt')
    result = result.query('number.str.contains(@number)', engine='python')
    result = result[0:1].values.tolist()
    result = itertools.chain(*result)
    result = list(result)

    if len(result) == 0 or number is re.sub("\\D", "", result[0]):
        if "en" in brt:
            return("scp-" + str(number) + "はまだ存在しません")
        else:
            return("scp-" + str(number) + "-" + str(brt) + "はまだ存在しません")

    return(result)
