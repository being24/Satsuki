# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import collections
import csv
import itertools
import logging.config
import os
import pprint
import random
import re
import sys
from datetime import datetime, timedelta

import discord
import pandas as pd
import requests
import zenhan
from pytz import timezone


class libbbbbbbb(object):
    def gen_url(msg):
        """Generate URL"""
        msg = zenhan.z2h(msg.casefold()).replace("-", "").replace("scp", "")

        number = re.sub("\\D", "", msg)
        if number is None:
            return None

        brt = msg.replace(number, "")

        if brt is "":
            brt = "en"

        if brt not in BRANCHS:
            reply = brt + "支部は存在しませんよ？"
            return reply

        quotient = int(number) / 1000 + 1
        quotient = int(quotient)
        if "ru" in brt:
            quotient = quotient - 1
        elif "ex" in brt:
            quotient = 1

        csvfile_name = brt + str(quotient)
        try:
            dictionary = pd.read_csv(currentpath + "/data/" + csvfile_name +
                                     ".csv", names=["url", "title"])
        except FileNotFoundError:
            if "en" in brt:
                return brt + "支部にはまだ対応していないか、もしくはscp-" + \
                    str(number) + "が対応するシリーズがまだ開放されていないかのどちらかです"

            else:
                return brt + "支部にはまだ対応していないか、もしくはscp-" + \
                    str(number) + "-" + str(brt) + "が対応するシリーズがまだ開放されていないかのどちらかです"

        result = dictionary[dictionary["url"].str.contains(str(number))]
        result = result.values.tolist()
        result = itertools.chain(*result)
        result = list(result)

        if len(result) == 0:
            if "en" in brt:
                return("scp-" + str(number) + "はまだ存在しません")
            else:
                return("scp-" + str(number) + "-" + str(brt) + "はまだ存在しません")

        return(result)
