from ._engine import async_session
from ._models import User

from datetime import date

from sqlalchemy.sql.expression import select, update, delete, case, func


async def registrate_if_not_exists(id_: int):
    async with async_session() as session:
        exists = (await session.execute(select(User.id).where(User.id == id_).limit(1))).one_or_none()
        if exists is None:
            user = User(id=id_)
            session.add(user)
            await session.commit()


async def delete_user(id_: int):
    query = delete(User).where(User.id == id_)

    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_user_advice_step(id_: int):
    query = select(User.advice_step).where(User.id == id_).limit(1)
    async with async_session() as session:
        advice_step = (await session.execute(query)).scalar_one_or_none()
    return advice_step


async def update_users_advice_step():
    query = update(User).values(advice_step=case((User.advice_step == 6, 0), else_=User.advice_step + 1))
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def update_user_birth_date(id_: int, birth_date: str):
    query = update(User).where(User.id == id_).values(birth_date=birth_date)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_apply_code(id_: int) -> str | None:
    query = select(User.apply_code).where(User.id == id_).limit(1)
    async with async_session() as session:
        apply_code = (await session.execute(query)).scalar_one_or_none()
    return apply_code


async def set_apply_code(id_: int, apply_code: str):
    query = update(User).where(User.id == id_).values(apply_code=apply_code)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def check_if_user_has_birth_date(id_: int) -> str | None:
    query = select(User.birth_date).where(User.id == id_).limit(1)
    async with async_session() as session:
        birth_date = (await session.execute(query)).scalar_one_or_none()
    return birth_date


async def set_horoscope_text_index(id_: int, i: int):
    query = update(User).where(User.id == id_).values(horoscope_text_index=i)
    async with async_session() as session:
        await session.execute(query)
        await session.commit()


async def get_horoscope_text_index(id_: int) -> int:
    query = select(User.horoscope_text_index).where(User.id == id_).limit(1)
    async with async_session() as session:
        index = (await session.execute(query)).scalar_one_or_none()
    return index


async def get_count_all_users() -> int:
    query = select(func.count('*')).select_from(User)
    async with async_session() as session:
        count = (await session.execute(query)).scalar_one()
    return count


async def users_for_today() -> int:
    query = select(func.count('*')).select_from(User).where(func.DATE(User.registration_date) == date.today())
    async with async_session() as session:
        count = (await session.execute(query)).scalar_one()
    return count
