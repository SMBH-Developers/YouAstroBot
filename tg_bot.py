import asyncio
import random
import logging
import re

from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram import executor, types, exceptions
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import markdown

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from loguru import logger
from zodiac_sign import get_zodiac_sign

from texts import random_texts_year, study_menu_texts
from texts import welcome_text, to_connect, start_texts, study_text, astro_advices
from keyboards import Markups
from bf_texts import bf_sending, SendingData
from src.common import settings
from src.models import db, db_sendings

class States(StatesGroup):
    get_user_date_for_horoscope_year = State()
    back_state = State()


storage = RedisStorage2(db=settings.redis_db, pool_size=40)
bot = Bot(settings.tg_token)
dp = Dispatcher(bot, storage=storage)
ADMIN_IDS = (1188441997, 791363343)
markups = Markups()

available_codes = list(range(15908, 531284))  # Коды для генерации заявки при окончании получения разбора гороскопа
horoscopes_padejs = {'Овен': 'Овна', 'Телец': 'Тельца', 'Близнецы': 'Близнецов', 'Рак': 'Раков',
                     'Лев': 'Льва', 'Дева': 'Девы', 'Весы': 'Весов', 'Скорпион': 'Скорпиона',
                     'Стрелец': 'Стрельца', 'Козерог': 'Козерога', 'Водолей': 'Водолея', 'Рыбы': 'Рыб'}
language = 'ru_RU'

#astro_advice_photo = "AgACAgIAAxkBAALh-GTb8V2CjeboPMbxCqT_X_RF0xuXAAJa0jEb1fvhSqtfMMzRcXDlAQADAgADeQADMAQ"
#astrology_is_photo = "AgACAgIAAxkBAALh-WTb8XC7Kgec83nd-cBmaeAKBvQdAAJc0jEb1fvhSqFeL9QHtyBIAQADAgADeQADMAQ"
#lune_horoscope_photo = "AgACAgIAAxkBAALh-mTb8X2CG2p51lcOPHSET0LG8zEKAAI2yzEbEB7gSuc24irJBkw_AQADAgADeQADMAQ"
#year_horoscope_photo = "AgACAgIAAxkBAALh-2Tb8Yi05TG0ZUHqoyjfbLjwOHKzAAJe0jEb1fvhSiVBtqT4X0zYAQADAgADeQADMAQ"
BF_PEOPLE = [791363343, 923202245, 1633990660, 1188441997, 627568042]


def get_value_of_arg(arg: str) -> str:
    """Получает значение из аргумент=значение"""
    return arg.split('=')[-1]


def generate_apply_code():
    code = ''.join(map(lambda num: str(num), [random.choice((4, 5, 6, 7, 8, 9)) for _ in range(6)]))
    return code


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['photo'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.photo[-1].file_id)


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['document'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.document.file_id)


@dp.message_handler(commands=['start'], state='*')
@logger.catch
async def start_mes(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await message.answer_photo(types.InputFile('data/photos/lune_horoscope.JPG'), welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')
    await db.registrate_if_not_exists(message.from_user.id)


@dp.message_handler(lambda message: message.from_user.id in BF_PEOPLE, commands=['bf_stat'], state='*')
async def get_bf_stat(message: types.Message):
    stat = await db_sendings.get_bf_stat()
    await message.answer(stat)


@dp.callback_query_handler(lambda call: call.data == 'delete_msg', state='*')
async def del_msg(call: types.CallbackQuery, state: FSMContext):
    """
    Удаляет сообщение как мусор
    """
    try:
        await call.message.delete()
    except exceptions.MessageCantBeDeleted:
        await call.message.delete_reply_markup()
        await call.answer('Невозможно удалить сообщение')


@dp.message_handler(lambda message: message.text == '👈Обратно', state="*")
@logger.catch
async def back_from_getting_horoscope_year(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer_photo(lune_horoscope_photo, welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')


@dp.message_handler(lambda message: message.text == '👈Назад', state='*')
@logger.catch
async def back_from_get_user_date_guide(message: types.Message, state: FSMContext):
    await message.answer(study_text, reply_markup=markups.study_mrkup)


@dp.message_handler(lambda message: message.text == '✨Получить бесплатный гороскоп на 2024 год', state='*')
@logger.catch
async def get_horoscope_on_2023_year(message: types.Message, state: FSMContext):
    user_date = await db.check_if_user_has_birth_date(message.from_user.id)
    if not bool(user_date):
        await bot.send_message(message.chat.id,
                               text='🙏Для получения гороскопа на год, пожалуйста, напишите дату рождения в форме дд.мм.гггг',
                               reply_markup=markups.to_menu_mrkup, parse_mode='html')
        await state.set_state(States.get_user_date_for_horoscope_year.state)
    else:
        day, month = user_date.split('.')[:2]
        zodiac = get_zodiac_sign(day, month, language='ru_RU')
        user_choose = await db.get_horoscope_text_index(message.from_user.id)
        await bot.send_message(message.chat.id, text=generate_beautiful_text('year', zodiac, user_date, user_choose),
                               reply_markup=markups.to_menu_mrkup,
                               parse_mode='html')
        await state.set_state(States.back_state.state)
        asyncio.create_task(send_text_with_inline_btn(message.chat.id))


@dp.message_handler(lambda message: message.text in start_texts, state='*')
@logger.catch
async def which_horoscope(message: types.Message, state) -> None:
    if message.text == '✨Получить бесплатный гороскоп':
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏Для получения гороскопа на год, пожалуйста, напишите дату рождения в форме дд.мм.гггг',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='ru_RU')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(types.InputFile('data/photos/year_horoscope.JPG'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '📜Образовательное меню':
        await message.answer(study_text, reply_markup=markups.study_mrkup)


async def generate_astro_advice(user_id):
    start_of_text = '✨Астрологический совет на день:'
    advice = astro_advices[await db.get_user_advice_step(user_id)]
    now_time = datetime.now()
    tomorrow_time = (now_time + timedelta(days=1))
    necessary_time = datetime(year=tomorrow_time.year, month=tomorrow_time.month, day=tomorrow_time.day, hour=0,
                              minute=0, second=0)
    left_time_for_update = round(((necessary_time - now_time).total_seconds() / 60 / 60), 1)
    end_of_text = f"❤️До появления нового астрологического совета осталось {left_time_for_update}ч."
    main_text = f'{start_of_text}\n\n{advice}\n\n{end_of_text}'
    return main_text


@dp.message_handler(lambda message: message.text in study_menu_texts or message.text in ('🙏Получить бесплатный гороскоп', '✨Получить бесплатный гороскоп на год', '✨Астро-совет на день'), state='*')
async def study_menu_dispatcher(message: types.Message, state: FSMContext):
    if message.text in ('🙏Получить бесплатный гороскоп', '✨Получить бесплатный гороскоп на год'):
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏Для получения гороскопа на год, пожалуйста, напишите дату рождения в форме дд.мм.гггг',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='ru_RU')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(photo=types.InputFile('data/photos/year_horoscope.JPG'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '✨Астро-совет на день':
        text = await generate_astro_advice(message.from_user.id)
        await message.answer_photo(types.InputFile('data/photos/astro_advice.JPG'), text, reply_markup=markups.mrkup_for_every_study_btn)
    elif message.text == '✨Что такое астрология?':
        await message.answer_photo(types.InputFile('data/photos/astrology_is.JPG'), study_menu_texts[message.text],
                                   reply_markup=markups.mrkup_for_every_study_btn)
    else:
        text = study_menu_texts[message.text]
        await message.answer(text, reply_markup=markups.mrkup_for_every_study_btn)


@dp.message_handler(lambda message: message.from_user.id in ADMIN_IDS, state='*', commands=['admin'])
@logger.catch
async def admin_menu(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(message.chat.id, text='Выберите действие', reply_markup=markups.admin_mrkup)


@dp.callback_query_handler(lambda call: call.from_user.id in ADMIN_IDS and call.data.startswith('Admin'), state='*')
@logger.catch
async def admin_calls(call: types.CallbackQuery, state: FSMContext) -> None:
    action = '_'.join(call.data.split('_')[1:])
    if action == 'Users_Total':
        await call.message.edit_text(text=f'Пользователей всего: {await db.get_count_all_users()}',
                                     reply_markup=markups.back_admin_mrkup)

    elif action == 'Users_For_TODAY':
        await call.message.edit_text(text=f'Пользователей за сегодня: {await db.users_for_today()}',
                                     reply_markup=markups.back_admin_mrkup)

    # elif action == 'Dates_For_TODAY':
    #     await call.message.edit_text(
    #         text=f'Пользователей, которые ввели дату за сегодня: {db.get_count_dates_for_today()}',
    #         reply_markup=markups.back_admin_mrkup)

    elif action == 'BACK':
        await call.message.edit_text(text='Выберите действие', reply_markup=markups.admin_mrkup)


def generate_beautiful_text(horoscope_type, zodiac, user_date, user_choose):
    main_text = '⭐️Гороскоп на '
    main_text += '2024 год'
    horoscope_text = random_texts_year[user_choose]
    main_text += f' для {markdown.hbold(horoscopes_padejs[zodiac])} | Дата рождения: {markdown.hbold(user_date)}\n\n{horoscope_text}' + to_connect
    return main_text


async def send_analyze_of_answers(chat_id, text_to_send):
    await asyncio.sleep(7)
    await bot.send_photo(chat_id, photo=types.InputFile('data/photos/year_horoscope.JPG'), caption=text_to_send, parse_mode='html')
    asyncio.create_task(send_text_with_inline_btn(chat_id))


async def send_text_with_inline_btn(chat_id):
    apply_code = await db.get_apply_code(chat_id)
    if apply_code is None:
        apply_code = generate_apply_code()
        await db.set_apply_code(chat_id, str(apply_code))
    await asyncio.sleep(2)  # 12106
    text = f"{markdown.hbold('🔆Только сегодня')} дипломированный астролог Вера {markdown.hbold('подготовит для Вас бесплатный')} персональный гороскоп на текущий год.\n\n📎Ваш кодовый номер заявки: {markdown.hcode(apply_code)}\n\nПожалуйста пришлите астрологу Вере кодовый номер заявки и место рождения на личный аккаунт — @Soull_Healerr👈\n\n{markdown.hbold('❗️Количество бесплатных мест ограничено')}"
    await bot.send_message(chat_id, text, parse_mode='html',
                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(
                               text='Написать астрологу', url=f'https://t.me/Soull_Healerr')]]))


@dp.message_handler(state=States.get_user_date_for_horoscope_year)
@logger.catch
async def choose_zodiac_year(message: types.Message, state: FSMContext) -> None:
    if re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{4}', message.text):
        day, month, year = message.text.split('.')
        if 0 < int(day) < 32 and 0 < int(month) < 13 and int(year) < 2023:
            await db.update_user_birth_date(message.from_user.id, message.text)
            zodiac = get_zodiac_sign(day, month, language='ru_RU')
            user_choose_year = random.choice(range(3, len(random_texts_year)))
            await db.set_horoscope_text_index(message.from_user.id, user_choose_year)
            await message.answer('🪄Обрабатываю информацию...', reply_markup=markups.to_menu_mrkup)
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_analyze_of_answers(message.chat.id,
                                                        generate_beautiful_text('year', zodiac, message.text,
                                                                                user_choose_year)))
        else:
            await message.answer('Некорректная дата!\n'
                                 '🙏Для получения гороскопа на год, пожалуйста, напишите дату рождения в форме дд.мм.гггг',
                                 reply_markup=markups.to_menu_mrkup)
    else:
        await message.answer('Неверный формат.\n'
                             '🙏Для получения гороскопа на год, пожалуйста, напишите дату рождения в форме дд.мм.гггг',
                             reply_markup=markups.to_menu_mrkup)


async def sending_messages_2h():
    while True:
        await asyncio.sleep(7)

        text_for_2h_autosending = f"{markdown.hbold('🙌Дорогие мои')}, я спешу сообщить о том, что {markdown.hbold('осталось всего 6 бесплатных мест')} на {markdown.hbold('бесплатное составление')} персонального гороскопа на текущий год\n\n{markdown.hbold('Не упустите')} свой шанс, {markdown.hbold('напишите астрологу')} Вере слово \"{markdown.hbold('Счастье')}\" в личные сообщения — @Soull_Healerr👈\n\n🧚С помощью {markdown.hbold('бесплатного персонального гороскопа')} мы сможем {markdown.hbold('выявить актуальные жизненные проблемы')} во всех сферах и {markdown.hbold('найти правильные пути')} для их решения"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("Впустить счастье✨", url="https://t.me/Soull_Healerr"))

        users = await db_sendings.get_users_2h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_for_2h_autosending, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got 2h_autosending')
                await db_sendings.mark_got_2h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_24_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_24h = f"🌖Здравствуйте, сегодня {markdown.hbold('Луна находится в самой благоприятной фазе')}, при которой можно сделать наиболее {markdown.hbold('точный индивидуальный астрологический разбор')} по натальной карте. В честь этого события — астролог {markdown.hbold('Вера подготовит для Вас бесплатный разбор.')}\n\n🧘‍♀️В нем Вы узнаете о том, какую {markdown.hbold('дорогу советуют выбрать звезды,')} как можно решить {markdown.hbold('текущие жизненные проблемы')} и избежать {markdown.hbold('дальнейших неудач')} в своем жизненном пути\n\nДля получения необходимо {markdown.hbold('написать дату')} и {markdown.hbold('место своего рождения')} в личные сообщения — @Soull_Healerr 👈\n\n{markdown.hbold('🔮Количество бесплатных мест ограничено!')}"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("🔆Бесплатный астрологический разбор", url="https://t.me/Soull_Healerr"))

        users = await db_sendings.get_users_24h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_autosending_24h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_24h')
                await db_sendings.mark_got_24h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_48_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_48h = f"🧚‍♂️Здравствуйте, в {markdown.hbold('этот замечательный день')} число моих {markdown.hbold('учеников')}, получивших {markdown.hbold('астрологическую консультацию')} в этом году — {markdown.hbold('превысило 1.500 человек')}\n\nВ честь такого {markdown.hbold('важного события')}, я хочу сделать {markdown.hbold('Вам подарок')} и сделать {markdown.hbold('бесплатный астрологический разбор🎉')}\n\nДля получения {markdown.hbold('бесплатного разбора')} — {markdown.hbold('напишите')} мне в личные сообщения {markdown.hbold('дату рождения')} — @Soull_Healerr👈\n\n🪄{markdown.hbold('Бесплатный разбор только для первых 10 написавших')}"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("Забрать подарок🎁", 
url="https://t.me/Soull_Healerr"))

        users_for_autosending_1 = await db_sendings.get_users_48h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text_autosending_48h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_text_48h')
                await db_sendings.mark_got_48h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_72h():
    while True:
        await asyncio.sleep(12)

        text = f'🪐Здравствуйте, хочу сообщить, что после {markdown.hbold("Ваших многочисленных просьб")} - я {markdown.hbold("открываю второй поток")} и {markdown.hbold("хочу подарить 15-ти")} счастливчикам {markdown.hbold("бесплатный астрологический разбор")}\n\n🙌Если Вы {markdown.hbold("готовы найти правильный путь в своей жизни")}, то напишите {markdown.hbold("дату рождения мне в личные сообщения — @Soull_Healerr👈")}'
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Получить разбор🔱", url="https://t.me/Soull_Healerr"))

        users_for_autosending_1 = await db_sendings.get_users_72h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text, parse_mode='html', reply_markup=kb)
                logger.info(f'ID: {user}. Got autosending_text_72h')
                await db_sendings.mark_got_72h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.exception(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


@dp.callback_query_handler(lambda call: call.data == 'black_friday?get_gift', state='*')
async def send_black_friday_gift(call: types.CallbackQuery, state: FSMContext):
    chat_member = await bot.get_chat_member(-1002059782974, call.from_user.id)
    if chat_member.is_chat_member():
        await call.message.answer_document('BQACAgIAAxkBAAFqLvZlShPPCzUoYZKx5RVGi3ibd2iT6wACHTUAAofGUUq9ksqFXr6WfjME')
    else:
        await call.answer("Войдите в марафон, чтобы получить подарок ❤️")


async def bf_task(id_: int, sending: SendingData, db_func, skip_if_chat_member: bool = False, only_for_chat_member: bool = False):
    try:

        if skip_if_chat_member or only_for_chat_member:
            chat_member = await bot.get_chat_member(-1002059782974, id_)
            if chat_member.is_chat_member() and skip_if_chat_member:
                return 'skip'
            elif not chat_member.is_chat_member() and only_for_chat_member:
                return 'skip'
            name = chat_member.user.first_name
        else:
            name = None

        #if id_ in skip_100_leads:
        #    return 'skip'

        text = await sending.get_text(bot, id_, name)
        if sending.photo is not None:
            await bot.send_photo(id_, types.InputFile(sending.photo), caption=text, reply_markup=sending.kb,
                                 parse_mode='html', disable_notification=True)
        else:
            await bot.send_message(id_, text=text, reply_markup=sending.kb,
                                   parse_mode='html', disable_web_page_preview=True)
        await db_func(id_)
        sending.count += 1
        logger.success(f'{id_} sending_{sending.uid} text')

    except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
        logger.exception(f'ID: {id_}. DELETED')
        await db.delete_user(id_)
    except Exception as e:
        logger.error(f'BUG: {e}')
    else:
        return 'success'
    return 'false'


async def sending_newsletter():
    white_day = 24
    now_time = datetime.now()

    if now_time.day > white_day:
        return

    while True:
        await asyncio.sleep(2)
        if now_time.day == white_day and now_time.hour >= 17:
            try:
                tasks = []
                users = [1371617744] + list(await db_sendings.get_users_for_sending_newsletter())
                print(len(users))
                for user in users:
                    logger.info(f"Пытаюсь отправить сообщение рассылки - {user}")
                    try:
                        _s = bf_sending
                        # if _s.count >= 80000:
                        #     break
                        tasks.append(asyncio.create_task(bf_task(user, _s, db_sendings.set_newsletter)))
                        if len(tasks) > 40:
                            print(len(tasks))
                            r = await asyncio.gather(*tasks, return_exceptions=False)
                            await asyncio.wait(tasks)
                            await asyncio.sleep(0.4)
                            logger.info(f"{r.count('success')=}", f"{r.count('false')=}", f"{r.count('skip')=}")
                            tasks.clear()

                    except Exception as ex:
                        logger.error(f'Ошибка в малом блоке sending: {ex}')
                    finally:
                        await asyncio.sleep(0.03)
            except Exception as ex:
                logger.error(f"Ошибка в большом блоке sending - {ex}")
            finally:
                await bot.send_message(1371617744, f"ERROR рассылка стопнулась.")
                logger.info("Рассылка завершилась")


async def on_startup(_):
    asyncio.create_task(sending_newsletter())
    asyncio.create_task(sending_messages_2h())
    asyncio.create_task(sending_message_24_h())
    asyncio.create_task(sending_message_48_h())
    asyncio.create_task(sending_message_72h())


async def update_db_advices_step_func():
    await db.update_users_advice_step()


try:
    a_logger = logging.getLogger('apscheduler.scheduler')
    a_logger.setLevel(logging.DEBUG)
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(trigger='cron', hour='00', minute='00', func=update_db_advices_step_func)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
finally:
    stop = True
    logger.info("Бот закончил работу")
