# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import typing
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import (Column, DateTime, Integer, String, and_, or_, select,
                        update)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

try:
    from .create_Postgre_engine import engine
except BaseException:
    import sys
    sys.path.append("../utils")
    from create_Postgre_engine import engine

Base = declarative_base()


@dataclass
class SCPArticleDatacls:
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


class SCPArticle(Base):
    __tablename__ = 'SCPArticle_infoBase'

    article_id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    metatitle = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    created_by = Column(String, nullable=False)
    created_by_unix = Column(String, nullable=False)
    created_by_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(String, nullable=True)
    updated_by_unix = Column(String, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    commented_at = Column(DateTime, nullable=True)
    commented_by = Column(String, nullable=True)
    commented_by_unix = Column(String, nullable=True)
    commented_by_id = Column(Integer, nullable=True)
    parent_fullname = Column(String, nullable=True)
    comments = Column(Integer, default=0)
    size = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    rating_votes = Column(Integer, nullable=False)
    revisions = Column(Integer, nullable=False)
    tags = Column(ARRAY(String), nullable=True)


class ArticleManager():
    def __init__(self) -> None:
        pass

    async def create_table(self) -> None:
        """テーブルを作成する関数
        """
        async with engine.begin() as conn:
            await conn.run_sync(SCPArticle.metadata.create_all)

    @staticmethod
    def return_dataclass(data: SCPArticle) -> SCPArticleDatacls:
        """SCPArticleからSCPArticleDataclsを生成する関数

        Args:
            data (SCPArticle)

        Returns:
            SCPArticleDatacls
        """
        db_data = data[0]
        processed_data = SCPArticleDatacls(
            article_id=db_data.article_id,
            fullname=db_data.fullname,
            title=db_data.title,
            metatitle=db_data.metatitle,
            created_at=db_data.created_at,
            created_by=db_data.created_by,
            created_by_unix=db_data.created_by_unix,
            created_by_id=db_data.created_by_id,
            updated_at=db_data.updated_at,
            updated_by=db_data.updated_by,
            updated_by_unix=db_data.updated_by_unix,
            updated_by_id=db_data.updated_by_id,
            commented_at=db_data.commented_at,
            commented_by=db_data.commented_by,
            commented_by_unix=db_data.commented_by_unix,
            commented_by_id=db_data.commented_by_id,
            parent_fullname=db_data.parent_fullname,
            comments=db_data.comments,
            size=db_data.size,
            rating=db_data.rating,
            rating_votes=db_data.rating_votes,
            revisions=db_data.revisions,
            tags=db_data.tags
        )

        return processed_data

    @staticmethod
    def return_DBClass(data: SCPArticleDatacls) -> SCPArticle:
        """SCPArticleDataclsからSCPArticleを作成する関数

        Args:
            data (SCPArticleDatacls):

        Returns:
            SCPArticle:
        """
        db_data = data
        processed_data = SCPArticle(
            article_id=db_data.article_id,
            fullname=db_data.fullname,
            title=db_data.title,
            metatitle=db_data.metatitle,
            created_at=db_data.created_at,
            created_by=db_data.created_by,
            created_by_unix=db_data.created_by_unix,
            created_by_id=db_data.created_by_id,
            updated_at=db_data.updated_at,
            updated_by=db_data.updated_by,
            updated_by_unix=db_data.updated_by_unix,
            updated_by_id=db_data.updated_by_id,
            commented_at=db_data.commented_at,
            commented_by=db_data.commented_by,
            commented_by_unix=db_data.commented_by_unix,
            commented_by_id=db_data.commented_by_id,
            parent_fullname=db_data.parent_fullname,
            comments=db_data.comments,
            size=db_data.size,
            rating=db_data.rating,
            rating_votes=db_data.rating_votes,
            revisions=db_data.revisions,
            tags=db_data.tags
        )

        return processed_data

    async def get_data_from_fullname(
            self, fullname: str) -> Union[SCPArticleDatacls, None]:
        """完全一致検索でDBからSCPArticleDataclsで１つ取り出す取り出す関数

        Args:
            fullname (str): カラムの値

        Returns:
            Union[SCPArticleDatacls, None]: あればSCPArticleDataclsなければNone
        """
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter_by(fullname=f"{fullname}")
                result = await session.execute(stmt).first()

                if result is None:
                    return None

                data = self.return_dataclass(result[0])
                return data

    async def get_data_from_fullname_ilike(
            self, fullname: str) -> Union[List[SCPArticleDatacls], None]:
        """部分一致検索でDBからSCPArticleDataclsのリストを取り出す関数


        Args:
            fullname (str): 探す文字列

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        fullname = fullname.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    SCPArticle.fullname.ilike(f'%{fullname}%'))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_all_ilike(self, all_: str) -> Union[List[SCPArticleDatacls], None]:
        """url・タイトル・著者から該当するデータのリストを作成する関数

        Args:
            all_ (str): Created_by_unixとcreated_byとtitleとfullname(部分一致)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        all_small = all_.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    or_(
                        SCPArticle.created_by_unix.ilike(f'%{all_small}%'),
                        SCPArticle.created_by.ilike(f'%{all_}%'),
                        SCPArticle.title.ilike(f'%{all_}%'),
                        SCPArticle.metatitle.ilike(f'%{all_}%'),
                        SCPArticle.fullname.ilike(f'%{all_small}%')))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_tags_and(
            self, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """タグが含まれるデータをDBからSCPArticleDataclsのリストを取り出す関数

        Args:
            tags (List[str]): タグのリスト

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    SCPArticle.tags.contains(tags))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_fullname_and_tag(self, fullname: str, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """tagとfullnameから該当するデータのリストを作成する関数

        Args:
            fullname (str): Url(部分一致)
            tags (List[str]): Tag(一致検索)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        fullname = fullname.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    and_(
                        SCPArticle.tags.contains(tags),
                        SCPArticle.fullname.ilike(f'%{fullname}%')))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_title_and_tag(self, title: str, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """tagとtitleから該当するデータのリストを作成する関数

        Args:
            title (str): title(部分一致)
            tags (List[str]): Tag(一致検索)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    and_(
                        SCPArticle.tags.contains(tags), or_(
                            SCPArticle.title.ilike(f'%{title}%'),
                            SCPArticle.metatitle.ilike(f'%{title}%'),)))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_author_and_tag(self, author: str, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """tagと著者から該当するデータのリストを作成する関数

        Args:
            author (str): Created_by_unix(部分一致)
            tags (List[str]): Tag(一致検索)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        author_small = author.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    and_(
                        SCPArticle.tags.contains(tags), or_(
                            SCPArticle.created_by_unix.ilike(
                                f'%{author_small}%'),
                            SCPArticle.created_by.ilike(f'%{author}%'))
                    ))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_all_and_tag(self, all_: str, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """tagとurl・タイトル・著者から該当するデータのリストを作成する関数

        Args:
            all_ (str): Created_by_unixとcreated_byとtitleとfullname(部分一致)
            tags (List[str]): Tag(一致検索)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        all_small = all_.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    and_(
                        SCPArticle.tags.contains(tags),
                        or_(
                            SCPArticle.created_by_unix.ilike(f'%{all_small}%'),
                            SCPArticle.created_by.ilike(f'%{all_}%'),
                            SCPArticle.title.ilike(f'%{all_}%'),
                            SCPArticle.metatitle.ilike(f'%{all_}%'),
                            SCPArticle.fullname.ilike(f'%{all_small}%'))))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_data_from_url_and_tag(self, url: str, tags: Union[List[str], typing.Tuple[str, ...]]) -> Union[List[SCPArticleDatacls], None]:
        """tagと著者から該当するデータのリストを作成する関数

        Args:
            url (str): fullname(部分一致)
            tags (List[str]): Tag(一致検索)

        Returns:
            Union[List[SCPArticleDatacls], None]: あればlistなければNone
        """
        url = url.casefold()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    and_(
                        SCPArticle.tags.contains(tags),
                        SCPArticle.fullname.ilike(f'%{url}%')
                    ))
                result = await session.execute(stmt)
                result = result.fetchall()

                if len(result) == 0:
                    return None

                data_list = [self.return_dataclass(data) for data in result]
                return data_list

    async def get_scp_random(self, tag: str) -> Optional[SCPArticleDatacls]:
        """scpタグ付きの記事をランダムで返す関数

        Args:
            tag (str): [支部タグを想定

        Returns:
            Optional[SCPArticleDatacls]: ランダムで一個
        """

        tags = ['scp']
        if tag != 'all':
            tags.append(tag)

        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(SCPArticle).filter(
                    SCPArticle.tags.contains(tags)).order_by(
                    func.random()).limit(1)
                result = await session.execute(stmt)
                result = result.fetchone()

                if result is not None:
                    data = self.return_dataclass(result)

                    return data


if __name__ == "__main__":
    article_mng = ArticleManager()

    loop = asyncio.get_event_loop()

    conn = loop.run_until_complete(engine.connect())
    result = loop.run_until_complete(
        article_mng.get_scp_random())
    loop.close()
    # asyncio.run(article_mng.create_table())
    if result is not None:
        for data in result:
            print(data.fullname)

    # print(asyncio.run(article_mng.get_data_from_tags_and(['メタデータ'])))
