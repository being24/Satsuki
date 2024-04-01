import pathlib

from sqlalchemy.ext.asyncio import create_async_engine

data_path = pathlib.Path(__file__).parents[1]
data_path /= "../data"
data_path = data_path.resolve()
db_path = data_path
db_path /= "./data.sqlite3"
engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
