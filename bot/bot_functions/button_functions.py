import random

from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, InlineKeyboardButton, URLInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot.DTO.data_to_object import Task, Employee


def bot_futter_buttons():
    keyboard = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text="👷 Ish olish")
    ]
    keyboard.add(*buttons)
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def choose_task_inline_buttons(state: FSMContext):
    markup = InlineKeyboardBuilder()
    task_ids = Task().select('id', status='free')
    task_id_list = []
    for i in task_ids:
        task_id_list.append(i[0])
    random_task_id = random.choice(task_id_list)
    task_code = Task().select('task_code', id=random_task_id)
    buttons = []
    buttons.append(InlineKeyboardButton(text=f"Ish", callback_data=f"task_choose_{random_task_id}"))
    # buttons.append(InlineKeyboardButton(text='⬅Orqaga', callback_data='↪Chiqish'))
    markup.add(*buttons)
    markup.adjust(2, repeat=True)
    return markup


async def task_show(state: FSMContext, task_id, employee_telegram_id):
    task_info = Task().select(id=task_id)
    # id_task = task_info
    task_markup = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text='Tanlash', callback_data=f"employee_task_choose_{task_id}_{employee_telegram_id}"),
    ]

    img = URLInputFile(url=task_info[0][1])
    caption = f"<b>Ish tavsifi:</b> <i>{task_info[0][2]}</i>" + f"\n<b>Ish kodi:</b> <i>{task_info[0][3]}</i>"
    task_markup.add(*buttons)
    task_markup.adjust(3, 2)
    task_markup = task_markup.as_markup()
    return (task_markup, img, caption)


def employee_id_inline_button():
    employees = Employee().select()
    buttons = []
    ikb = InlineKeyboardBuilder()
    for employee in employees:
        buttons.append(
            InlineKeyboardButton(text=f"{employee[0]}", callback_data=f"employee_detail_{employee[0]}")
        )
    buttons.append(InlineKeyboardButton(text="⬅Orqaga", callback_data='↪Chiqish'))
    ikb.add(*buttons)
    ikb.adjust(5, repeat=True)
    return ikb.as_markup()


def employee_edit_id_inline_button():
    employees = Employee().select()
    buttons = []
    ikb = InlineKeyboardBuilder()
    for employee in employees:
        buttons.append(
            InlineKeyboardButton(text=f"{employee[0]}", callback_data=f"employee_edit_{employee[0]}")
        )
    ikb.add(*buttons)
    ikb.adjust(5, repeat=True)
    return ikb.as_markup()


def employee_confirmation(employee_telegram_id):
    ikb = InlineKeyboardBuilder()
    buttons = []
    buttons.append(
        InlineKeyboardButton(text='⛳Yakunlash', callback_data=f'employee_finished_task_{employee_telegram_id}'))
    ikb.add(*buttons)
    return ikb.as_markup()


def admin_confirmation():
    ikb = InlineKeyboardBuilder()
    ikb.add(
        InlineKeyboardButton(text='✅Bajarildi', callback_data='admin_confirm'),
        InlineKeyboardButton(text='❌Bajarilmadi', callback_data='admin_ignore')
    )
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


def task_id_inline_button():
    tasks = Task().select()
    buttons = []
    ikb = InlineKeyboardBuilder()
    for task in tasks:
        buttons.append(
            InlineKeyboardButton(text=f"{task[0]}", callback_data=f"task_detail_{task[0]}")
        )
    buttons.append(InlineKeyboardButton(text="⬅Orqaga", callback_data='↪Chiqish'))
    ikb.add(*buttons)
    ikb.adjust(5, repeat=True)
    return ikb.as_markup()


async def task_edit_id_inline_button(state: FSMContext):
    ikb = InlineKeyboardBuilder()
    buttons = []
    data = await state.get_data()
    task_code = data['task_code']
    tasks = Task().select(task_code=task_code)
    for task in tasks:
        buttons.append(
            InlineKeyboardButton(text=f"{task[0]}", callback_data=f"task_edit_{task[0]}")
        )
    ikb.add(*buttons)
    ikb.adjust(4, repeat=True)
    return ikb.as_markup()


async def task_delete_id_inline_button(state: FSMContext):
    ikb = InlineKeyboardBuilder()
    buttons = []
    data = await state.get_data()
    task_code = data['task_code']
    tasks = Task().select(task_code=task_code, status='free') + Task().select(task_code=task_code, status='done')
    for task in tasks:
        buttons.append(
            InlineKeyboardButton(text=f"{task[0]}", callback_data=f"task_delete_{task[0]}")
        )
    ikb.add(*buttons)
    ikb.adjust(4, repeat=True)
    return ikb.as_markup()


def adminka_back_button():
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='⬅orqaga', callback_data='↪Chiqish'))
    return ikb.as_markup()


def employee_empty_task_back():
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='⬅orqaga', callback_data='empty_task_back'))
    return ikb.as_markup()


def admin_task_edit_button():
    ikb = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="➕Ish qo'shish", callback_data="➕Ish qo'shish"),
        InlineKeyboardButton(text="❌Ishni o'chirish", callback_data="❌Ishni o'chirish"),
        InlineKeyboardButton(text="💱Ishni tahrirlash", callback_data="💱Ishni tahrirlash"),
        InlineKeyboardButton(text="↪Chiqish", callback_data="↪Chiqish")
    ]
    ikb.add(*buttons)
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def admin_employee_edit_button():
    ikb = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="➕Ishchi qo'shish", callback_data="➕Ishchi qo'shish"),
        InlineKeyboardButton(text="❌Ishchini o'chirish", callback_data="❌Ishchini o'chirish"),
        InlineKeyboardButton(text="💱Ishchini tahrirlash", callback_data="💱Ishchini tahrirlash"),
        InlineKeyboardButton(text="↪Chiqish", callback_data="↪Chiqish")
    ]
    ikb.add(*buttons)
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def task_update_field():
    ikb = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text='Rasmi', )
    ]


def admin_type():
    ikb = InlineKeyboardBuilder()
    buttons = [

        InlineKeyboardButton(text='Admin', callback_data='admin_@'),
        InlineKeyboardButton(text='Buyurtmachi', callback_data='moderator_@'),
        InlineKeyboardButton(text='Monoblok', callback_data='monoblok_@')

    ]
    ikb.add(*buttons)
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()
