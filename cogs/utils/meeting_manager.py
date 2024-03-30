# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from dataclasses import dataclass
import datetime
from typing import List, Optional, Union

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, DATETIME, INTEGER, VARCHAR

from .create_SQLIte_engine import engine

Base = declarative_base()


@dataclass
class ReserveData:
    msg_id: int
    draft_title: str
    draft_link: str
    author_name: str
    reserve_time: datetime.datetime


class ReserveDataDB(Base):
    __tablename__ = 'ReserveData'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    msg_id = Column(BIGINT, nullable=False)
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
            msg_id=data.msg_id,
            draft_title=data.draft_title,
            draft_link=data.draft_link,
            author_name=data.author_name,
            reserve_time=data.reserve_time)
        return db_data_raw

    @staticmethod
    def return_DB_obj(msg_id: int, data: ReserveData) -> ReserveDataDB:
        """dataclassからDBのデータを作成する関数

        Args:
            data (ReserveData): dataclass

        Returns:
            ReserveDataDB: DB型
        """

        new_reserve = ReserveDataDB(
            msg_id=msg_id,
            draft_title=data.draft_title,
            draft_link=data.draft_link,
            author_name=data.author_name,
            reserve_time=data.reserve_time)

        return new_reserve

    async def insert_many_nijiru(self, data_list: List[ReserveData]) -> None:
        """煮汁システムから取得した予約データを格納する関数

        Args:
            data_list (List[ReserveData]): データのリスト(msg_idを入力する欄は0)
        """

        DB_data_list = [self.return_DB_obj(0, data) for data in data_list]
        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    session.add_all(DB_data_list)
                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

    async def add_reserve_data(self, data: ReserveData) -> None:
        """煮汁システムから取得した予約データを格納する関数

        Args:
            data_list (List[ReserveData]): データのリスト(msg_idを入力する欄は0)
        """

        msg_id = data.msg_id
        db_data = self.return_DB_obj(msg_id, data)

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    session.add(db_data)
                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

    async def get_reserve_data_from_date(self, date_jst: datetime.datetime) -> Optional[List[ReserveData]]:
        """指定された日の予約データを取得する関数

        Args:
            date_jst (datetime.datetime): 時間（これから日を計算する）

        Returns:
            Optional[List[ReserveData]]: 予約データのリスト
        """

        first = date_jst.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date_jst.replace(hour=23, minute=59, second=59, microsecond=0)

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    stmt = select(ReserveDataDB).filter(
                        and_(
                            (ReserveDataDB.reserve_time >= first),
                            (ReserveDataDB.reserve_time <= end))).order_by(
                        ReserveDataDB.reserve_time)
                    result = await session.execute(stmt)
                    result = result.all()
                    result = [
                        self.return_dataclass(
                            data[0]) for data in result]

                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

        if len(result) == 0:
            return None
        else:
            return result

    async def upsert_and_return_reserve_data(self, jst_time: datetime.datetime, ReserveData_list: List[ReserveData]) -> Optional[List[ReserveData]]:
        """nijiruのデータとDBのデータを比較して、存在しないものを追加後、今日の分のデータを返す関数

        Args:
            jst_time (datetime): ３時間ずれたdatetime
            ReserveData_list (List[ReserveData]): RSSから取得したデータ

        Returns:
            Optional[List[ReserveData]]: 今日の予約リスト
        """

        data_from_db = await self.get_reserve_data_from_date(jst_time)

        write_list = []
        if data_from_db is not None:
            db_url_list = [data.draft_link for data in data_from_db]
            for data in ReserveData_list:
                if data.draft_link not in db_url_list:
                    write_list.append(data)
        else:
            write_list = ReserveData_list

        await self.insert_many_nijiru(write_list)

        data_from_db = await self.get_reserve_data_from_date(jst_time)
        return data_from_db


if __name__ == "__main__":
    setting_mng = MeetingManager()
    asyncio.run(setting_mng.create_table())

    # asyncio.run(setting_mng.register_setting())

    result = asyncio.run(setting_mng.get_guild_ids())
    print((result))
