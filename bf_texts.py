from dataclasses import dataclass, field
from string import Template

from aiogram import types, Bot
from aiogram.utils import markdown as m


@dataclass
class SendingData:
    uid: str
    text: str | Template
    url: str
    btn_title: str
    photo: str | None = None

    kb: types.InlineKeyboardMarkup = field(init=False)
    count: int = field(init=False)

    async def get_text(self, bot: Bot, user_id: int, name: str = None):
        if isinstance(self.text, str):
            return self.text
        else:
            if name is None:
                chat_member = await bot.get_chat_member(user_id, user_id)
                name = chat_member.user.first_name
            name = m.quote_html(name)
            return self.text.substitute(name=name)

    def __post_init__(self):
        self.kb = types.InlineKeyboardMarkup()
        self.kb.add(types.InlineKeyboardButton(self.btn_title, url=self.url))
        # self.kb.add(types.InlineKeyboardButton('🎁 Получить подарок', url=self.url))
        # self.kb.add(types.InlineKeyboardButton('🎁 Получить подарок', callback_data="black_friday?get_gift"))
        self.count = 0


bf_sending = SendingData("sending_24_april",
                         Template(f'🛳ТВОЯ РОСКОШНАЯ ЖИЗНЬ НАЧИНАЕТСЯ СЕГОДНЯ\n\n 24.04.2024 Зеркальная Дата отправит тебя в самое увлекательное путешествие в мире денег ✈️\n\n Ведь именно сегодня самый лучший день для того, чтобы наладить денежный поток, благодаря которому твоя жизнь полностью поменяется. \n\n Пиши мне в личные сообщения, я расскажу как использовать эту возможность @Soul_Healerr \n\n Роскошная жизнь ждет тебя 🛩🏝'),
                         url="https://t.me/Soul_Healerr",
                         btn_title="ИЗМЕНИТЬ СВОЮ ЖИЗНЬ"
                         )
