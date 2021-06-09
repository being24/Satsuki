# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import pathlib
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

root_path = pathlib.Path(__file__).parents[2]

dotenv_path = root_path / '.env'

load_dotenv(dotenv_path)

DATABASE = 'postgresql'
DBAPI = 'asyncpg'
USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DB_NAME = os.getenv('POSTGRES_DB')

CONNECT_STR = f'{DATABASE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'

engine = create_async_engine(CONNECT_STR)

'''
loop = asyncio.new_event_loop()
conn = loop.run_until_complete(engine.connect())
loop.run_until_complete(conn.close())
loop.close()
'''
