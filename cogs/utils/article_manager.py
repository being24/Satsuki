# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, DATETIME, INTEGER, VARCHAR

Base = declarative_base()



@dataclass
class ArticleData:
    article_id: int
    fullname: str
    title: str
    metatitle: str
    created_at: datetime
    created_by: str
    created_by_unix: str
    created_by_id: int
    updated_at: datetime
    updated_by: str
    updated_by_unix: str
    updated_by_id: int
    commented_at: datetime
    commented_by: str
    commented_by_unix: str
    commented_by_id: int
    parent_fullname: str
    comments: int
    size: int
    rating: int
    rating_votes: int
    revisions: int
    tags: List[str]


class ArticleDataDB(Base):
    __tablename__ = 'SCPArticle_infoBase'

    article_id = Column(BIGINT, primary_key=True)
    fullname = Column(VARCHAR, nullable=False, primary_key=True)
    title = Column(VARCHAR, nullable=False)
    metatitle = Column(VARCHAR, nullable=True)
    created_at = Column(DATETIME, nullable=False)
    created_by = Column(VARCHAR, nullable=False)
    created_by_unix = Column(VARCHAR, nullable=False)
    created_by_id = Column(BIGINT, nullable=False)
    updated_at = Column(DATETIME, nullable=True)
    updated_by = Column(VARCHAR, nullable=True)
    updated_by_unix = Column(VARCHAR, nullable=True)
    updated_by_id = Column(BIGINT, nullable=True)
    commented_at = Column(DATETIME, nullable=True)
    commented_by = Column(VARCHAR, nullable=True)
    commented_by_unix = Column(VARCHAR, nullable=True)
    commented_by_id = Column(BIGINT, nullable=True)
    parent_fullname = Column(VARCHAR, nullable=True)
    comments = Column(INTEGER, nullable=True)
    size = Column(INTEGER, nullable=False)
    rating = Column(INTEGER, default=0)
    rating_votes = Column(INTEGER, default=0)
    revisions = Column(INTEGER, default=0)
    tags = Column(VARCHAR, default='')


class SettingManager():
    def __init__(self):
        data_path = pathlib.Path(__file__).parents[1]
        data_path /= '../data'
        data_path = data_path.resolve()
        db_path = data_path
        db_path /= './data.sqlite3'
        self.engine = create_async_engine(
            f'sqlite+aiosqlite:///{db_path}', echo=True)

    async def create_table(self) -> None:
        """テーブルを作成する関数
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    def return_dataclass(data: ArticleDataDB) -> ArticleData:
        """DBからの情報をデータクラスに変換する関数、もうちょっとなんとかならんか？？？

        Args:
            data (ArticleDataDB): DBから持ってきたデータ
        Returns:
            ArticleData: dataclass
        """
        tag_list = [
            str(tags) for tags in data['tags'].split(' ') if id != '']
        db_data_raw = ArticleData(
            article_id=data.article_id,
            fullname=data.fullname,
            title=data.title,
            metatitle=data.metatitle,
            created_at=data.created_at,
            created_by=data.created_by,
            created_by_unix=data.created_by_unix,
            created_by_id=data.created_by_id,
            updated_at=data.updated_at,
            updated_by=data.updated_by,
            updated_by_unix=data.updated_by_unix,
            updated_by_id=data.updated_by_id,
            commented_at=data.commented_at,
            commented_by=data.commented_by,
            commented_by_unix=data.commented_by_unix,
            commented_by_id=data.commented_by_id,
            parent_fullname=data.parent_fullname,
            comments=data.comments,
            size=data.size,
            rating=data.rating,
            rating_votes=data.rating_votes,
            revisions=data.revisions,
            tags=tag_list)
        return db_data_raw

    @staticmethod
    def return_DB_obj(data: ArticleData) -> ArticleDataDB:
        """dataclassからDBのデータを作成する関数

        Args:
            data (ArticleData): dataclassからArticleDataDBを返す関数

        Returns:
            ArticleDataDB: DB型
        """
        tags = (' ').join(data.tags)
        new_article = ArticleDataDB(
            article_id=data.article_id,
            fullname=data.fullname,
            title=data.title,
            metatitle=data.metatitle,
            created_at=data.created_at,
            created_by=data.created_by,
            created_by_unix=data.created_by_unix,
            created_by_id=data.created_by_id,
            updated_at=data.updated_at,
            updated_by=data.updated_by,
            updated_by_unix=data.updated_by_unix,
            updated_by_id=data.updated_by_id,
            commented_at=data.commented_at,
            commented_by=data.commented_by,
            commented_by_unix=data.commented_by_unix,
            commented_by_id=data.commented_by_id,
            parent_fullname=data.parent_fullname,
            comments=data.comments,
            size=data.size,
            rating=data.rating,
            rating_votes=data.rating_votes,
            revisions=data.revisions,
            tags=tags)

        return new_article

    '''
    async def is_exist(self, guild_id: int) -> bool:
        """主キーであるギルドIDが存在するかを判定する関数

       Args:
            guild_id(int): サーバーID

        Returns:
            bool: あったらTrue、なかったらFalse
        """
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                stmt = select(GuildSettingDB).where(
                    GuildSettingDB.guild_id == guild_id)
                result = await session.execute(stmt)
                result = result.fetchone()
                if result is not None:
                    return True
                else:
                    return False
    '''

    async def get_guild(self, guild_id: int) -> Union[GuildSetting, None]:
        async with AsyncSession(self.engine, expire_on_commit=True) as session:
            async with session.begin():
                stmt = select(GuildSettingDB).where(
                    GuildSettingDB.guild_id == guild_id)
                result = await session.execute(stmt)
                result = result.fetchone()

                if result is None:
                    return None

                guildsetting = GuildSetting(
                    result[0].guild_id,
                    result[0].dispander,
                    result[0].welcome_msg,
                    result[0].black_server)

        return guildsetting

    async def get_guild_ids(self) -> Union[None, List[int]]:
        """DBに存在する全てのサーバーのidを取得する関数

        Returns:
            Union[None, List[int]]: なければNone、あればintのlist
        """
        async with AsyncSession(self.engine, expire_on_commit=True) as session:
            async with session.begin():
                stmt = select(GuildSettingDB)
                result = await session.execute(stmt)
                result = result.all()

                if result is None:
                    return None
                else:
                    ids = [guild[0].guild_id for guild in result]
                    return ids

    async def init_guilds(self, guild_ids: List[int]):
        """起動時にサーバごとの設定を補完する関数

        Args:
            guild_ids (List[int]): 現在参加しているサーバーのリスト
        """
        exists_ids = await self.get_guild_ids()
        for guild_id in guild_ids:
            if guild_id not in exists_ids:
                await self.register_guild(guild_id)

    async def set_black_list(self, server_id: int):
        """ブラックリストのサーバーを追加する関数

        Args:
            server_id (int): ブラックリストのサーバーのID
        """
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                stmt = update(GuildSettingDB).where(
                    GuildSettingDB.guild_id == server_id).values(
                    black_server=True)
                await session.execute(stmt)

    async def remove_black_list(self, server_id: int):
        """ブラックリストのサーバーを削除する関数

        Args:
            server_id (int): ブラックリストのサーバーのID
        """
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                stmt = update(GuildSettingDB).where(
                    GuildSettingDB.guild_id == server_id).values(
                    black_server=False)
                await session.execute(stmt)


if __name__ == "__main__":
    setting_mng = SettingManager()
    asyncio.run(setting_mng.create_table())

    # asyncio.run(setting_mng.register_setting())

    result = asyncio.run(setting_mng.get_guild_ids())
    print((result))
