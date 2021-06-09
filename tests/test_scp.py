# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase, main

import bot
from cogs.scp_cog import SCPArticleCog as scp


class Test(TestCase):
    def setup(self):
        self.scp = scp(bot)

    def test_from_struct_time_to_datetime(self):
        self.setup()
        test_patterns = [
            ("173", ('173', 'en')),
            ("173jp", ('173', 'jp')),
            ("173cn", ('173', 'cn')),
            ("173cna", ('173', 'cna')),
            ("cn173", ('173', 'cn')),
            ("cn17123", (None, None)),
        ]
        for num_brt, expected_result in test_patterns:
            with self.subTest(num_brt=num_brt):
                self.assertEqual(
                    scp.prosess_arg(self.scp, num_brt=num_brt), expected_result)
                pass


if __name__ == '__main__':
    main()
