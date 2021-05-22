# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import pathlib
from dataclasses import dataclass
import datetime
from typing import List, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, DATETIME, INTEGER, VARCHAR

from .create_SQLIte_engine import engine

Base = declarative_base()


@dataclass
class ReserveData:
    draft_title: str
    draft_link: str
    author_name: str
    reserve_time: datetime.datetime


class ReserveDataDB(Base):
    d_today = str(datetime.date.today())
    __tablename__ = d_today

    msd_id = Column(BIGINT, primary_key=True)
    draft_title = Column(VARCHAR, nullable=True)
    draft_link = Column(VARCHAR, nullable=False)
    author_name = Column(VARCHAR, nullable=False)
    reserve_time = Column(DATETIME, nullable=False)


class MeetingManager():
    def __init__(self):
        pass

    async def create_table(self) -> None:
        """テーブルを作成する関数
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    def return_dataclass(data: ReserveDataDB) -> ReserveData:
        """DBからの情報をデータクラスに変換する関数、もうちょっとなんとかならんか？？？

        Args:
            data (ReserveDataDB): DBから持ってきたデータ
        Returns:
            ReserveData: dataclass
        """

        db_data_raw = ReserveData(
            draft_title=data.draft_title,
            draft_link=data.draft_link,
            author_name=data.author_name,
            reserve_time=data.reserve_time)
        return db_data_raw

    @staticmethod
    def return_DB_obj(msg_id: int, data: ReserveData) -> ReserveDataDB:
        """dataclassからDBのデータを作成する関数

        Args:
            data (ReserveData): dataclassからReserveDataDBを返す関数

        Returns:
            ReserveDataDB: DB型
        """

        new_reserve = ReserveDataDB(
            msd_id=msg_id,
            draft_title=data.draft_title,
            draft_link=data.draft_link,
            author_name=data.author_name,
            reserve_time=data.reserve_time)

        return new_reserve


if __name__ == "__main__":
    setting_mng = MeetingManager()
    asyncio.run(setting_mng.create_table())

    # asyncio.run(setting_mng.register_setting())

    result = asyncio.run(setting_mng.get_guild_ids())
    print((result))
