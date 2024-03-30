# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import pathlib

from sqlalchemy.ext.asyncio import create_async_engine

data_path = pathlib.Path(__file__).parents[1]
data_path /= '../data'
data_path = data_path.resolve()
db_path = data_path
db_path /= './data.sqlite3'
engine = create_async_engine(
    f'sqlite+aiosqlite:///{db_path}', echo=True)

loop = asyncio.get_event_loop()
conn = loop.run_until_complete(engine.connect())
loop.run_until_complete(conn.close())
