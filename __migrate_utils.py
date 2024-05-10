import pymysql
import asyncio
import asyncssh
import aiomysql
import json

from sqlalchemy.sql.expression import update

from src.models import User, async_session

# *mdb - mariadb


async def get_users_from_mdb():
    async with asyncssh.connect(host='45.12.213.205', port=22, username='root', password='IZci0ba7Mas1', known_hosts=None) as conn:
        async with conn.forward_local_port('127.0.0.1', 0, '127.0.0.1', 3306) as tunnel:
            local_bind_port = tunnel.get_port()
            print('used query')
            query = "SELECT userId, createdAt, Advice_Step, User_Horoscope_Date, Year_text, apply_code, Got_2h_autosending, Got_autosending_1, Got_48h_autosending, Got_72h_autosending FROM Users;"
            connection = await aiomysql.connect(host='localhost',  user='root', password='root', db='horoscope', port=local_bind_port)
            cur = await connection.cursor()
            await cur.execute(query)
            data = await cur.fetchall()
            await cur.close()
            connection.close()
    return data


async def fill_psql_from_mdb_data(data):
    users = [User(id=int(user[0]), registration_date=user[1], advice_step=user[2],
                  birth_date=user[3], horoscope_text_index=user[4], apply_code=user[5],
                  got_2h_autosending=user[6], got_24h_autosending=user[7],
                  got_48h_autosending=user[8], got_72h_autosending=user[9]
                  ) for user in data]
    async with async_session() as session:
        session.add_all(users)
        await session.commit()


async def update_stages_via_ignore_list():
    async with async_session() as session:
        with open('data/ignore_list.json') as f:
            ls = json.load(f)
        await session.execute(update(User).where(User.id.in_(ls)).values(stage='stage_4'))
        await session.commit()


async def main():
    # await update_stages_via_ignore_list()
    data = await get_users_from_mdb()
    await fill_psql_from_mdb_data(data)


if __name__ == '__main__':
    asyncio.run(main())

