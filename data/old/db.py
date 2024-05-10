import pymysql
import aiomysql
from pymysql.connections import Connection


class Database:

    @staticmethod
    def connect() -> Connection:
        """

        :return: Connection
        """

        connection: Connection = pymysql.connect(
            user="root", passwd="root", host="localhost", database='horoscope',
            port=3306, autocommit=True)
        return connection

    @staticmethod
    async def async_connect():
        connection = await aiomysql.connect(user="root", password="root", host="localhost", db='horoscope', port=3306, autocommit=True)
        return connection

    def register_user(self, user_id: int | str, referal) -> None:
        query_to_reg_user = f"INSERT INTO Users (userId, referal) VALUES ({user_id}, %s);"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_reg_user, (referal,))

    def check_if_user_exists(self, user_id: int | str) ->  bool:
        query_to_get_user = f"SELECT userId FROM Users WHERE userId='{user_id}' LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_user)
                user = cursor.fetchone()
        if not user:
            return False
        return True

    def check_if_user_has_date(self, user_id):
        query = f"SELECT User_Horoscope_Date from Users where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                date = cursor.fetchone()[0]
        return date

    def update_user_date(self, user_id, date):
        query = f"UPDATE Users SET User_Horoscope_Date=%s, When_got_date=NOW() WHERE userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (date,))

    def get_count_all_users(self) -> int:
        query_to_get_users_id = "SELECT COUNT(*) FROM Users;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_users_id)
                count_users = cursor.fetchone()[0]
        return count_users

    def get_all_users(self) -> tuple:
        query_to_get_users_id = "SELECT userId FROM Users;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_users_id)
                users = cursor.fetchall()
        return users

    def get_users_with_step(self, step: int) -> tuple:
        query_to_get_users_id = f"SELECT userId FROM Users WHERE step=%s;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_users_id, (step,))
                users = cursor.fetchall()
        return users

    def user_for_today(self) -> int:
        query_to_get_users_for_today = "SELECT COUNT(*) FROM Users WHERE Date(createdAt)=CURDATE();"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_users_for_today)
                count_users = cursor.fetchone()[0]
        return count_users

    def update_step(self, user_id: int | str) -> None:
        query_to_update_user_step = f"UPDATE Users SET step=step+1 WHERE userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_update_user_step)

    def get_count_users_with_step(self, step: str) -> int:
        query_to_get_count_users_with_step = f"SELECT COUNT(*) FROM Users WHERE step={step};"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_count_users_with_step)
                count_users = cursor.fetchone()[0]
        return count_users

    def update_user_year_text(self, user_id: int, user_choose: int) -> None:
        query = f"UPDATE Users SET Year_text={user_choose} where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

    def update_user_day_text(self, user_id: int, user_choose: int) -> None:
        query = f"UPDATE Users SET Day_text={user_choose} where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

    def select_year_text(self, user_id):
        query = f"SELECT Year_text from Users where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                info = cursor.fetchone()[0]
        return info

    def select_day_text(self, user_id):
        query = f"SELECT Day_text from Users where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                info = cursor.fetchone()[0]
        return info

    def get_count_dates_for_today(self):
        query = "SELECT COUNT(*) FROM Users WHERE Date(When_got_date)=CURDATE();"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                count = cursor.fetchone()[0]
        return count

    def delete_user(self, user):
        query_to_update_user_step = f"DELETE FROM Users WHERE userId={user} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_update_user_step)

    async def async_del(self, user):
        query = f"DELETE FROM Users WHERE userId={user} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        # await cursor.execute(query)
        await connection.ensure_closed()

    def get_users_for_autosending_1(self):
        query_to_get_users_for_sending = "SELECT userId FROM Users where Old_auditory=0 AND TIMESTAMPDIFF(DAY, Got_2h_autosending, NOW())>=1 AND Got_autosending_1 IS NULL;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_to_get_users_for_sending)
                users = cursor.fetchall()
        return [int(user_id[0]) for user_id in users]

    async def mark_got_autosending_1(self, user_id):
        query = f"UPDATE Users SET Got_autosending_1=NOW() WHERE userId={user_id} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        await connection.ensure_closed()

    def get_users_2h_autosending(self):
        query = "SELECT userId FROM Users WHERE Got_2h_autosending IS NULL AND TIMESTAMPDIFF(MINUTE, createdAt, NOW())<=4290 AND  TIMESTAMPDIFF(MINUTE, createdAt, NOW())>=127;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
        return [int(user_id[0]) for user_id in users]

    async def mark_got_2h_autosending(self, user_id):
        query = f"UPDATE Users SET Got_2h_autosending=NOW() WHERE userId={user_id} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        await connection.ensure_closed()

    def get_users_48h_autosending(self):
        query = "SELECT userId FROM Users WHERE Got_48h_autosending IS NULL AND TIMESTAMPDIFF(DAY, Got_autosending_1, NOW())>=2 AND DATE(createdAt)>='2023-07-11';"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
        return [int(user_id[0]) for user_id in users]

    async def mark_got_48h_autosending(self, user_id):
        query = f"UPDATE Users SET Got_48h_autosending=NOW() WHERE userId={user_id} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        await connection.ensure_closed()

    def get_users_72h_autosending(self):
        query = "SELECT userId FROM Users WHERE Got_72h_autosending IS NULL AND TIMESTAMPDIFF(HOUR, Got_48h_autosending, NOW())>=25 AND DATE(createdAt)>='2023-10-31';"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
        return [int(user_id[0]) for user_id in users]

    async def mark_got_72h_autosending(self, user_id):
        query = f"UPDATE Users SET Got_72h_autosending=NOW() WHERE userId={user_id} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        await connection.ensure_closed()

    def get_all_users_from_who_got_answer(self):
        query = "SELECT COUNT(*) FROM Users WHERE Got_answer_on_2h_autosending IS NOT NULL;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                count = cursor.fetchone()[0]
        return count

    def set_got_answer_from_user(self, user_id):
        query = f"UPDATE Users SET Got_answer_on_2h_autosending=NOW() WHERE userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

    def get_nec_users(self):
        query = "SELECT userId from Users WHERE Got_2h_autosending  IS NOT NULL AND Got_answer_on_2h_autosending IS NULL;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
        return [int(user_id[0]) for user_id in users]

    def get_user_advice_step(self, user_id):
        query = f"SELECT Advice_Step from Users where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                advice_step = cursor.fetchone()[0]
        return advice_step

    def update_users_advice_step(self):
        query_1 = "UPDATE Users SET Advice_Step=IF(Advice_Step=6, 0, Advice_Step+1);"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_1)

    def set_apply_code(self, id_: int, code: str):
        query = f"UPDATE Users SET apply_code=%s WHERE userId={id_} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (code,))

    def get_apply_code(self, user_id):
        query = f"SELECT apply_code from Users where userId={user_id} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                apply_code = cursor.fetchone()[0]
        return apply_code

    def get_users_black_friday_sending(self):
        query = "SELECT userId FROM Users WHERE black_friday_sending IS NULL AND TIMESTAMPDIFF(DAY, createdAt, NOW())>=150 ORDER BY createdAt DESC LIMIT 30000;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
        print(f'got users {len(users)}')
        return [int(user_id[0]) for user_id in users]

    def get_black_friday_count(self) -> int:
        query = "SELECT COUNT(*) FROM Users WHERE black_friday_sending IS NOT NULL;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                count = cursor.fetchone()[0]
        return count

    def set_black_friday(self, id_: int, bf_state: str | None):
        query = f"UPDATE Users SET black_friday_sending=NOW(), bf_state=%s WHERE userId={id_} LIMIT 1;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (bf_state,))

    def get_bf_uid_count(self, uid: str):
        query = "SELECT COUNT(*) FROM Users WHERE bf_state=%s;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (uid,))
                count = cursor.fetchone()[0]
        return count

    async def async_set_black_friday(self, id_: int, bf_state: str | None):
        if bf_state is not None:
            bf_state = f"'{bf_state}'"
        else:
            bf_state = 'NULL'
        query = f"UPDATE Users SET black_friday_sending=NOW(), bf_state={bf_state} WHERE userId={id_} LIMIT 1;"
        connection = await self.async_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
        await connection.ensure_closed()

    def get_bf_stat(self) -> dict:
        query = "select count(*), bf_state from Users WHERE black_friday_sending is not null GROUP BY bf_state;"
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                stat: tuple[tuple] = cursor.fetchall()

        dict_stat = dict(stat)
        return dict_stat
