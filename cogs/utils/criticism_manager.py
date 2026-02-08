import asyncio
import datetime
from zoneinfo import ZoneInfo

from pydantic.dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, DATETIME, INTEGER, VARCHAR

from .create_SQLIte_engine import engine

Base = declarative_base()


@dataclass
class ReserveData:
    reserve_id: int
    title: str
    link: str
    author_id: int
    reserve_time: datetime.datetime


class ReserveDataDB(Base):
    __tablename__ = "ReserveData"

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    title = Column(VARCHAR, nullable=False)
    link = Column(VARCHAR, nullable=False)
    author_id = Column(BIGINT, nullable=False)
    reserve_time = Column(DATETIME, nullable=False)


class CriticismManager:
    def __init__(self):
        self.utc_zoneinfo = ZoneInfo("UTC")
        pass

    async def create_table(self) -> None:
        """テーブルを作成する関数"""
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

        reserve_time = data.reserve_time.replace(tzinfo=ZoneInfo("UTC"))

        reserve = ReserveData(
            reserve_id=data.id,
            title=data.title,
            link=data.link,
            author_id=data.author_id,
            reserve_time=reserve_time,
        )
        return reserve

    @staticmethod
    def return_DB_obj(data: ReserveData) -> ReserveDataDB:
        """dataclassからDBのデータを作成する関数

        Args:
            data (ReserveData): dataclass

        Returns:
            ReserveDataDB: DB型
        """

        reserve = ReserveDataDB(
            title=data.title,
            link=data.link,
            author_id=data.author_id,
            reserve_time=data.reserve_time,
        )

        return reserve

    async def add_reserve_data(self, data: ReserveData) -> None:
        """modalから受け取ったデータをDBに格納する関数

        Args:
            data (ReserveData): _description_
        """

        db_data = self.return_DB_obj(data)

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    session.add(db_data)
                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

    async def get_reserve_data_from_date(
        self, start: datetime.datetime, end: datetime.datetime
    ) -> list[ReserveData] | None:
        """指定された日の予約データを取得する関数

        Args:
            start (datetime.datetime): 取得開始日時
            end (datetime.datetime): 取得終了日時

        Returns:
            list[ReserveData]: 予約データのリスト
        """

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    stmt = (
                        select(ReserveDataDB)
                        .filter(
                            and_(
                                (ReserveDataDB.reserve_time >= start),
                                (ReserveDataDB.reserve_time <= end),
                            )
                        )
                        .order_by(ReserveDataDB.reserve_time)
                    )
                    result = await session.execute(stmt)
                    result = result.all()
                    result = [self.return_dataclass(data[0]) for data in result]

                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

        if len(result) == 0:
            return None
        else:
            return result

    async def get_reserve_data_from_date_and_id(
        self, user_id: int, start: datetime.datetime, end: datetime.datetime
    ) -> list[ReserveData] | None:
        """IDと日付から予約データを取得する関数

        Args:
            user_id (int): ユーザーID
            start (datetime.datetime): 取得開始日時
            end (datetime.datetime): 取得終了日時

        Returns:
            list[ReserveData]: 予約データのリスト
        """

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    stmt = (
                        select(ReserveDataDB)
                        .filter(
                            and_(
                                (ReserveDataDB.reserve_time >= start),
                                (ReserveDataDB.reserve_time <= end),
                                (ReserveDataDB.author_id == user_id),
                            ),
                        )
                        .order_by(ReserveDataDB.reserve_time)
                    )
                    result = await session.execute(stmt)
                    result = result.all()
                    result = [self.return_dataclass(data[0]) for data in result]

                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

        if len(result) == 0:
            return None
        else:
            return result

    async def get_reserve_data_from_id(self, reserve_id: int) -> None | ReserveData:
        """IDから予約データを取得する関数

        Args:
            reserve_id (int): 予約ID

        Returns:
            None | ReserveData: 予約データ
        """

        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    stmt = select(ReserveDataDB).filter(ReserveDataDB.id == reserve_id)
                    result = await session.execute(stmt)
                    result = result.all()
                    if len(result) == 0:
                        return None
                    result = self.return_dataclass(result[0][0])

                except BaseException:
                    await session.rollback()
                    raise
                else:
                    await session.commit()

    # async def upsert_and_return_reserve_data(
    #     self, jst_time: datetime.datetime, ReserveData_list: list[ReserveData]
    # ) -> Optional[list[ReserveData]]:
    #     """nijiruのデータとDBのデータを比較して、存在しないものを追加後、今日の分のデータを返す関数

    #     Args:
    #         jst_time (datetime): ３時間ずれたdatetime
    #         ReserveData_list (list[ReserveData]): RSSから取得したデータ

    #     Returns:
    #         Optional[list[ReserveData]]: 今日の予約リスト
    #     """

    #     data_from_db = await self.get_reserve_data_from_date(jst_time)

    #     write_list = []
    #     if data_from_db is not None:
    #         db_url_list = [data.draft_link for data in data_from_db]
    #         for data in ReserveData_list:
    #             if data.draft_link not in db_url_list:
    #                 write_list.append(data)
    #     else:
    #         write_list = ReserveData_list

    #     await self.insert_many_nijiru(write_list)

    #     data_from_db = await self.get_reserve_data_from_date(jst_time)
    #     return data_from_db


if __name__ == "__main__":
    setting_mng = CriticismManager()
    asyncio.run(setting_mng.create_table())
