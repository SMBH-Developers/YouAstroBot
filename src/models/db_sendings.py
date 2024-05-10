from ._engine import async_session
from ._models import User

from datetime import timedelta, datetime

from sqlalchemy import text, func
from sqlalchemy.sql.expression import select, update, or_



async def get_users_2h_autosending():
    async with async_session() as session:
        users = (await session.execute(select(User.id).where(
            func.extract('HOUR', func.now() - User.registration_date).between(2, 18),
            User.got_2h_autosending.is_(None)
                                                         )
                                      )
                 ).scalars().all()
    return users


async def mark_got_2h_autosending(id_):
    query = update(User).values(got_2h_autosending=func.now()).where(User.id == id_)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_users_24h_autosending():
    async with async_session() as session:
        users = (await session.execute(select(User.id).where(
            func.extract('HOUR', func.now() - User.got_2h_autosending).between(24, 48),
            User.got_24h_autosending.is_(None)
                                                         )
                                      )
                 ).scalars().all()
    return users


async def mark_got_24h_autosending(id_):
    query = update(User).values(got_24h_autosending=func.now()).where(User.id == id_)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_users_48h_autosending():
    async with async_session() as session:
        users = (await session.execute(select(User.id).where(
            func.extract('HOUR', func.now() - User.got_24h_autosending).between(24, 48),
            User.got_48h_autosending.is_(None)
                                                         )
                                      )
                 ).scalars().all()
    return users


async def mark_got_48h_autosending(id_):
    query = update(User).values(got_48h_autosending=func.now()).where(User.id == id_)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_users_72h_autosending():
    async with async_session() as session:
        users = (await session.execute(select(User.id).where(
            func.extract('HOUR', func.now() - User.got_48h_autosending).between(24, 48),
            User.got_72h_autosending.is_(None)
                                                         )
                                      )
                 ).scalars().all()
    return users


async def mark_got_72h_autosending(id_):
    query = update(User).values(got_72h_autosending=func.now()).where(User.id == id_)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_bf_stat() -> str:
    query = select(func.count('*').label('count'), User.bf_state).select_from(User)\
        .where(User.black_friday_sending.is_not(None)).group_by(User.bf_state)
    async with async_session() as session:
        stat = (await session.execute(query)).all()
    text = '\n'.join([f'{bf_stat.bf_state}{bf_stat.count}' for bf_stat in stat])
    return text


# async def get_bf_uid_count(uid: str):
#     query = select(func.count('*')).select_from(User).where(User.bf_state == uid)
#     async with async_session() as session:
#         count = (await session.execute(query)).scalar_one()
#     return count
#
#
# async def get_black_friday_count() -> int:
#     query = select(func.count('*')).select_from(User).where(User.black_friday_sending.is_not(None))
#     async with async_session() as session:
#         count = (await session.execute(query)).scalar_one()
#     return count


async def get_users_for_sending_newsletter() -> list[int]:
    query = select(User.id).where(
                                  User.sending_24_april.is_(None),
                                  (User.registration_date + timedelta(days=10)) < datetime.now()
                                  ).order_by(User.registration_date.desc())
    async with async_session() as session:
        users = (await session.execute(query)).scalars().all()
    return users


async def set_newsletter(id_: int):
    query = update(User).where(User.id == id_).values(sending_24_april=func.now())
    async with async_session() as session:
        await session.execute(query)
        await session.commit()
