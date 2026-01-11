"""ページデータ型定義"""

from pydantic import BaseModel, Field


class PageVote(BaseModel):
    """投票データ"""

    userId: int
    userName: str
    value: int  # +1 or -1
    recordedAt: int  # UNIXタイムスタンプ


class PageFile(BaseModel):
    """ファイルデータ"""

    wikidotFileId: int
    name: str
    url: str
    mimeType: str
    size: int


class PageListItem(BaseModel):
    """記事一覧アイテム"""

    wikidotId: int
    fullname: str
    name: str
    category: str
    title: str
    rating: int
    votesCount: int
    ratingPercent: float | None = None
    createdById: int | None = None
    createdByName: str | None = None
    createdAt: int
    updatedAt: int | None = None
    tags: list[str] = Field(default_factory=list)
    snippet: str | None = None


class Pagination(BaseModel):
    """ページネーション情報"""

    page: int
    perPage: int
    total: int
    totalPages: int


class PageListResponse(BaseModel):
    """記事一覧レスポンス"""

    status: str
    data: list[PageListItem]
    pagination: Pagination


class PageDetail(BaseModel):
    """記事詳細"""

    wikidotId: int
    fullname: str
    name: str
    category: str
    title: str
    rating: int
    votesCount: int
    ratingPercent: float | None = None
    createdById: int | None = None
    createdByName: str | None = None
    createdAt: int
    updatedById: int | None = None
    updatedByName: str | None = None
    updatedAt: int | None = None
    currentRevisionNo: int
    tags: list[str] = Field(default_factory=list)
    parentFullname: str | None = None
    commentsCount: int
    size: int


class PageDetailData(BaseModel):
    """記事詳細レスポンスのデータセクション"""

    page: PageDetail
    votes: list[PageVote]
    files: list[PageFile]
    latestSource: str | None = None


class PageDetailResponse(BaseModel):
    """記事詳細レスポンス"""

    status: str
    data: PageDetailData
