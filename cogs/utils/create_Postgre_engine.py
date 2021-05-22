# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

DATABASE = 'postgresql'
DBAPI = 'asyncpg'
USER = 'postgres'
PASSWORD = 'example'
HOST = '192.168.0.7'
PORT = '5432'
DB_NAME = 'ScpData'

CONNECT_STR = f'{DATABASE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'

engine = create_async_engine(CONNECT_STR)

loop = asyncio.new_event_loop()
conn = loop.run_until_complete(engine.connect())
loop.run_until_complete(conn.close())
loop.close()
