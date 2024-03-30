# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase, main

import pytz
from cogs.critique_meeting import CritiqueCog as mt


class Test(TestCase):
    def test_from_struct_time_to_datetime(self):
        naivetime = datetime(2021, 6, 8, 10, 27, 31)
        awaretime = pytz.utc.localize(naivetime)
        test_patterns = [
            ("Tue, 08 Jun 2021 10:27:31 +0000", awaretime),
            ("Tue, 08 Jun 2021 25:27:31 +0000", None),
            ("other", None),
        ]
        for struct_time, expected_result in test_patterns:
            with self.subTest(struct_time=struct_time):
                self.assertEqual(mt.from_struct_time_to_datetime(struct_time=struct_time), expected_result)


if __name__ == '__main__':
    main()
