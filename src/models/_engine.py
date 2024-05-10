from ..common import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine(settings.sqlalchemy_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)
