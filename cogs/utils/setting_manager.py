# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import pathlib
from dataclasses import dataclass
from typing import List, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import exists
from sqlalchemy.sql.sqltypes import BOOLEAN, Boolean
from sqlalchemy.types import BigInteger

Base = declarative_base()


# 鯖ごとに設定を変えられるようにする

@dataclass
class GuildSetting:
    guild_id: int
    dispander: bool
    welcome_msg: bool
    black_server: bool


class GuildSettingDB(Base):
    __tablename__ = 'guild_setting'

    guild_id = Column(BigInteger, primary_key=True)  # サーバーID
    dispander = Column(Boolean, default=True)  # メッセージ展開の可否
    welcome_msg = Column(Boolean, default=False)  # ウェルカムメッセージの可否
    black_server = Column(Boolean, default=False)  # 自動退出の対象か？


class SettingManager():
    def __init__(self):
        data_path = pathlib.Path(__file__).parents[1]
        data_path /= '../data'
        data_path = data_path.resolve()
        db_path = data_path
        db_path /= './data.sqlite3'
        self.engine = create_async_engine(
            f'sqlite:///{db_path}', echo=True)

    async def create_table(self) -> None:
        """テーブルを作成する関数
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            try:
                await self._init_setting()
            except BaseException:
                pass

    async def _init_setting(self) -> None:
        async with AsyncSession(self.engine, expire_on_commit=True) as session:
            async with session.begin():
                new_setting = GuildSettingDB(index=True)
                session.add(new_setting)

    async def register_guild(self, guild_id: int) -> None:
        """ギルドの設定を登録する関数

        Args:
            guild_id (int): サーバーID
            bot_manager_id (int): BOT管理者役職のID
            bot_user_id (int): BOT使用者役職のID
        """
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                new_guild = GuildSettingDB(
                    guild_id=guild_id)

                session.add(new_guild)

    '''
    async def update_guild(self, guild_id: int) -> None:
        """ギルドの設定を更新する関数

        Args:
            guild_id (int): サーバーID
            bot_manager_id (int): bot管理者のID
            bot_user_id (int): bot操作者のID
        """
        async with AsyncSession(self.engine) as session:
            async with session.begin():
                stmt = update(GuildSettingDB).where(
                    GuildSettingDB.guild_id == guild_id).values(
                    bot_manager_id=bot_manager_id,
                    bot_user_id=bot_user_id)
                await session.execute(stmt)
    '''

    async def is_exist(self, guild_id: int) -> bool:
        """主キーであるギルドIDが存在するかを判定する関数

        Args:
            guild_id (int): サーバーID

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

    async def get_guild(self, guild_id: int) -> Union[GuildSetting, None]:
        """ギルドの情報をGuildSettingで返す関数

        Args:
            guild_id (int): サーバーID

        Returns:
            GuildSetting: サーバの設定のデータクラス
        """
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
