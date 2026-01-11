"""ページAPI クライアント"""

import logging
import random
import time
import traceback
from enum import Enum
from os import getenv
from pathlib import Path
from pprint import pprint
from typing import Callable

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError

try:  # 通常のパッケージ実行
    from .page_models import (
        PageDetailResponse,
        PageListItem,
        PageListResponse,
    )
except ImportError:  # スタンドアロン実行時のフォールバック
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from cogs.utils.page_models import (
        PageDetailResponse,
        PageListItem,
        PageListResponse,
    )

logger = logging.getLogger("discord")

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


class SortField(str, Enum):
    """ソートフィールド"""

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    RATING = "rating"
    TITLE = "title"


class SortOrder(str, Enum):
    """ソート順序"""

    ASC = "asc"
    DESC = "desc"


def with_retry(
    func: Callable[[], httpx.Response],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> httpx.Response:
    """HTTPXレスポンスのリトライラッパー。

    冪等なGET用途想定で、429/5xxと接続エラーを指数バックオフ＋ジッターで再試行する。
    Retry-Afterがあればそれを優先する。
    """

    def _calc_delay(response: httpx.Response, attempt: int) -> float:
        header = response.headers.get("Retry-After")
        if header and header.isdigit():
            return float(header)

        jitter = random.uniform(0, base_delay)
        return base_delay * (2**attempt) + jitter

    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response = func()

            if response.status_code in RETRY_STATUS_CODES and attempt < max_retries:
                delay = _calc_delay(response, attempt)
                logger.warning(
                    "リトライ %s/%s: ステータス %s、%.2f秒後に再試行",
                    attempt + 1,
                    max_retries,
                    response.status_code,
                    delay,
                )
                time.sleep(delay)
                continue

            return response

        except httpx.RequestError as exc:  # 接続系の一時エラーを再試行
            last_exception = exc
            if attempt < max_retries:
                delay = base_delay * (2**attempt) + random.uniform(0, base_delay)
                logger.warning(
                    "リトライ %s/%s: 接続エラー %s、%.2f秒後に再試行",
                    attempt + 1,
                    max_retries,
                    type(exc).__name__,
                    delay,
                )
                time.sleep(delay)
            else:
                raise

    if last_exception:
        raise last_exception

    raise RuntimeError("Unexpected retry loop exit")


class PageSearchQuery:
    """ページ検索クエリビルダー"""

    def __init__(self):
        self.params: dict[str, str] = {}

    def by_query(self, q: str) -> "PageSearchQuery":
        """タイトルまたはfullnameで検索（部分一致）

        Args:
            q: 検索キーワード（タイトルまたはfullnameに部分一致）

        Note:
            APIは title と fullname の両方を検索します
        """
        self.params["q"] = q
        return self

    def by_author(self, author: str) -> "PageSearchQuery":
        """著者名で検索"""
        self.params["author"] = author
        return self

    def include_all_categories(self, include: bool = True) -> "PageSearchQuery":
        """全カテゴリを含めるか（デフォルトは_defaultのみ）

        Args:
            include: True = 全カテゴリ, False = _defaultのみ
        """
        self.params["include_all_categories"] = "true" if include else "false"
        return self

    def by_tags(
        self, *tags: str, and_tags: list[str] | None = None
    ) -> "PageSearchQuery":
        """タグで検索

        Args:
            *tags: タグ（OR条件）
            and_tags: AND条件のタグ

        Example:
            query.by_tags("tale", "keter", and_tags=["scp", "jp"])
            → +scp +jp tale keter
        """
        tag_parts = []

        # AND条件のタグ
        if and_tags:
            tag_parts.extend(f"+{tag}" for tag in and_tags)

        # OR条件のタグ
        tag_parts.extend(tags)

        self.params["tags"] = " ".join(tag_parts)
        return self

    def by_rating(
        self, min_val: int | None = None, max_val: int | None = None
    ) -> "PageSearchQuery":
        """評価値でフィルタ"""
        if min_val is not None:
            self.params["rating_min"] = str(min_val)
        if max_val is not None:
            self.params["rating_max"] = str(max_val)
        return self

    def sort_by(
        self,
        field: SortField,
        order: SortOrder = SortOrder.DESC,
    ) -> "PageSearchQuery":
        """ソート指定

        Args:
            field: ソートフィールド（SortField）
            order: ソート順序（SortOrder）
        """
        self.params["sort"] = field.value
        self.params["order"] = order.value
        return self

    def paginate(self, page: int = 1, per_page: int = 50) -> "PageSearchQuery":
        """ページネーション"""
        self.params["page"] = str(page)
        self.params["per_page"] = str(per_page)
        return self

    def build(self) -> dict[str, str]:
        """クエリパラメータを取得"""
        return self.params.copy()


class PageAPIClient:
    """ページデータ API クライアント

    APIを使用するため認証が必須です。
    APIキーは環境変数から自動的に読み込まれます。
    """

    def __init__(self, site: str = "scp-jp"):
        """初期化

        Args:
            site: Wikidot unix名（デフォルト: scp-jp）

        環境変数要件:
            PANOPTICON_API_URL: APIベースURL（例: https://manage.scp-jp.com）
            PANOPTICON_API_KEY: APIキー（manage API用）
        """
        dotenv_path = Path(__file__).parents[2] / ".env"
        if not dotenv_path.exists():
            raise FileNotFoundError(".env file not found")

        load_dotenv(dotenv_path)

        # APIキー（PANOPTICON_API_KEY
        panopticon_api_key = getenv("PANOPTICON_API_KEY")
        if panopticon_api_key is None:
            raise FileNotFoundError(
                "Panopticon API key not found! Set PANOPTICON_API_KEY in .env"
            )

        panopticon_api_url = getenv("PANOPTICON_API_URL")
        if panopticon_api_url is None:
            raise FileNotFoundError("Panopticon API URL not found error!")

        self.api_url = panopticon_api_url.rstrip("/")
        self.site = site
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {panopticon_api_key}"}
            if panopticon_api_key
            else {}
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    def search(self, query: PageSearchQuery | None = None) -> PageListResponse:
        """記事一覧検索

        Args:
            query: PageSearchQuery オブジェクト

        Returns:
            ページリスト
        """
        params = query.build() if query else {}

        # デフォルト値設定
        if "page" not in params:
            params["page"] = "1"
        if "per_page" not in params:
            params["per_page"] = "50"

        logger.debug(f"Search params: {params}")

        def request():
            return self.client.get(
                f"{self.api_url}/api/pages",
                params=params,
            )

        response = with_retry(request)

        if response.status_code != 200:
            logger.error(f"Failed to fetch pages: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise RuntimeError(f"API error: {response.status_code}")

        pprint(response.json())

        try:
            data = PageListResponse(**response.json())
            return data
        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise

    def search_all(self, query: PageSearchQuery) -> list[PageListItem]:
        """全ページ取得（ページネーション自動処理）

        Args:
            query: PageSearchQuery オブジェクト

        Returns:
            全ページリスト
        """
        all_pages: list[PageListItem] = []
        page = 1

        while True:
            query_copy = PageSearchQuery()
            query_copy.params = query.params.copy()
            query_copy.paginate(page=page, per_page=100)

            pages = self.search(query_copy)
            if not pages:
                break

            all_pages.extend(pages.data)
            logger.info(
                f"Fetched {len(pages.data)} pages (page {page}, total: {len(all_pages)})"
            )
            page += 1

        return all_pages

    def get_detail(self, page_id: int) -> PageDetailResponse | None:
        """記事詳細取得

        Args:
            page_id: Wikidot ページID

        Returns:
            詳細レスポンス（page, votes, files, latestSource）
        """

        def request():
            return self.client.get(f"{self.api_url}/api/pages/{page_id}")

        response = with_retry(request)

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            logger.error(f"Failed to fetch page detail: {response.status_code}")
            raise RuntimeError(f"API error: {response.status_code}")

        try:
            data = PageDetailResponse(**response.json())
            return data
        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise


if __name__ == "__main__":
    try:
        with PageAPIClient(site="scp-jp") as client:
            # 部分一致検索のテスト
            print("=== 検索（'オリジナル'を含む） + rating順 ===")
            query = (
                PageSearchQuery()
                .by_query("オリジナル")
                .sort_by(SortField.RATING, SortOrder.DESC)
            )
            print(f"Query params: {query.build()}")
            pages = client.search(query)
            print(f"Found {len(pages.data)} pages:")
            for item in pages.data[:5]:
                print(
                    f"- {item.title} (fullname={item.fullname}, rating={item.rating})"
                )

            print("\n=== 検索（'173'を含む） + _defaultのみ + rating順 ===")
            query2 = (
                PageSearchQuery()
                .by_query("173")
                .sort_by(SortField.RATING, SortOrder.DESC)
            )
            print(f"Query params: {query2.build()}")
            pages2 = client.search(query2)
            print(f"Found {len(pages2.data)} pages:")
            for item in pages2.data[:5]:
                print(f"- {item.title} (fullname={item.fullname}, rating={item.rating}")

            if not pages and not pages2:
                print("No pages found for any query.")
    except Exception:
        print("Search failed.")
        traceback.print_exc()
