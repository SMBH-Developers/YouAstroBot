from aiogram import types


class Markups:
    start_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_mrkup.add(types.KeyboardButton(text='✨Получить бесплатный гороскоп'))
    start_mrkup.add(types.KeyboardButton(text='📜Образовательное меню'))

    study_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    study_btns_titles = ['✨Что такое астрология?', '✨Гороскоп — что это?',
                         '✨Как появился первый гороскоп?', '✨Астро-совет на день',
                         '✨Что изучают в астрологии?', '✨Что такое 12 домов в астрологии?',
                         '✨Какой дом отвечает за работу?', '✨Какой дом отвечает за семью?',
                         '🙏Получить бесплатный гороскоп']

    study_mrkup.add(types.KeyboardButton('✨Что такое астрология?'), types.KeyboardButton('✨Гороскоп — что это?'))
    study_mrkup.add(types.KeyboardButton('✨Как появился первый гороскоп?'), types.KeyboardButton('✨Астро-совет на день'))
    study_mrkup.add(types.KeyboardButton('✨Что изучают в астрологии?'), types.KeyboardButton('✨Что такое 12 домов в астрологии?'))
    study_mrkup.add(types.KeyboardButton('✨Какой дом отвечает за работу?'), types.KeyboardButton('✨Какой дом отвечает за семью?'))
    study_mrkup.add(types.KeyboardButton('🙏Получить бесплатный гороскоп'))

    mrkup_for_every_study_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mrkup_for_every_study_btn.add(types.KeyboardButton('✨Получить бесплатный гороскоп на год'))
    mrkup_for_every_study_btn.add(types.KeyboardButton('👈Назад'))

    to_menu_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    to_menu_mrkup.add(types.KeyboardButton('📜Образовательное меню'))

    kb_if_how_to_get_know_zodiac = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='✨Получить бесплатный гороскоп на 2024 год'))
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='👈Назад'))

    admin_mrkup = types.InlineKeyboardMarkup()
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей всего', callback_data='Admin_Users_Total'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей за сегодня', callback_data='Admin_Users_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Ввели дату за сегодня', callback_data='Admin_Dates_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Зашли после рассылки 17ого марта 19:15', callback_data='Admin_17_march_sending'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка', callback_data='Admin_Send_Messages'))  # Рассылка по любым
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка тем, кто еще не перешёл', callback_data='Admin_Special_Send_Msgs'))  # Раcсылка только по тем, кто не перешёл на наш аккаунт
    admin_mrkup.add(types.InlineKeyboardButton(text='Перешедших по реф ссылкам', callback_data='Admin_Referal_Users'))
    back_admin_mrkup = types.InlineKeyboardMarkup()
    back_admin_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))

    @staticmethod
    def generate_send_msgs_step(sending_type: str) -> types.InlineKeyboardMarkup:
        send_messages_step_mrkup = types.InlineKeyboardMarkup()
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Первая ступень', callback_data=f'Sending?Step=0&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Вторая ступень', callback_data=f'Sending?Step=1&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Третья ступень', callback_data=f'Sending?Step=2&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Четвёртая ступень', callback_data=f'Sending?Step=3&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Отправить всем', callback_data=f'Sending?Step=ALL&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))
        return send_messages_step_mrkup

    back_to_steps = types.InlineKeyboardMarkup()
    back_to_steps.add(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='Admin_Send_Messages'))

    cancel_sending = types.InlineKeyboardMarkup()
    cancel_sending.add(types.InlineKeyboardButton(text='Отмена!', callback_data='Cancel_Getting_Msg_For_Sending'))

    to_our_tg_mrkup = types.InlineKeyboardMarkup()
    to_our_tg_mrkup.add(types.InlineKeyboardButton(text='ПОЛУЧИТЬ ГОРОСКОП', url=f'https://t.me/Soull_Healerr'))


    @staticmethod
    def generate_delete_msg_mrkup(arg=None):
        mrkup_to_del_msg = types.InlineKeyboardMarkup()
        mrkup_to_del_msg.add(types.InlineKeyboardButton('Закрыть', callback_data=f'delete_msg{arg if arg else ""}'))
        return mrkup_to_del_msg

    mrkup_referal_program = types.InlineKeyboardMarkup()
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨Проверить выполнение условий', callback_data='ref_program?check_reqs'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨Посмотреть отзывы', callback_data='ref_program?reviews'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨Как правильно пригласить друзей?', callback_data='ref_program?guide'))
