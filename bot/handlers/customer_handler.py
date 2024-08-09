import requests
from aiogram import Router, F
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, URLInputFile

from bot.DTO.data_to_object import Task
from bot.bot_commands.all_commands import SIMPLE_ADMINS
from bot.bot_functions.button_functions import admin_task_edit_button, task_edit_id_inline_button, \
    task_delete_id_inline_button, adminka_back_button
from bot.handlers.admin_handler import TaskUpdateForm, TaskAddForm
from bot.states import GetTaskIDForm
from bot.states.all_states import GetListTaskCode, GetEditTaskCode, GetDeleteTaskCode

customer_router = Router()

customer_router.message.filter(F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(SIMPLE_ADMINS))


@customer_router.message(Command(commands=['ishlar_royxati']))
async def lis_of_task_handler(message: Message, state: FSMContext):
    await state.set_state(GetListTaskCode.task_code)
    await message.answer(text="""
<b>Ishlarni ko'rish uchun ish kodini kiriting!
Masalan(N-250)</b>

""",
                         parse_mode=ParseMode.HTML)


@customer_router.message(GetListTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
async def task_id_handler(message: Message, state: FSMContext):
    await state.update_data(task_code=message.text)
    data = await state.get_data()
    task_code = data['task_code']
    session_task = Task().select(task_code=task_code)
    text = ""
    if session_task:
        for task_info in list(session_task):
            text += (f"""
<b>ID:</b>  <i>{task_info[0]}</i>
<b>Ish tavsifi:</b>  <i>{task_info[2]}</i>
<b>Ish kodi:</b>  <i>{task_info[3]}</i>\n
        """)
        await message.answer(text, reply_markup=adminka_back_button(), parse_mode=ParseMode.HTML)
    else:
        await message.answer("Kechirasiz bunday ID li ish mavjud emas🤕")


@customer_router.message(Command('ish_qoshish'))
async def add_task_button_handler(message: Message):
    await message.answer("Ish bo'limiga xush kelibsiz quyidagilardan qay birini tanlaysiz",
                         reply_markup=admin_task_edit_button())


@customer_router.callback_query(F.data == "❌Ishni o'chirish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetDeleteTaskCode.task_code)
    await callback.message.answer('<b>Ishni kodini kiriting🔢(Masalan: N-252)</b>', parse_mode=ParseMode.HTML)


@customer_router.message(GetDeleteTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
async def photo_handler(message: Message, state: FSMContext):
    await state.update_data(task_code=message.text)
    data = await state.get_data()
    task_code = data['task_code']
    task_info = Task().select(task_code=task_code, status='free') + Task().select(task_code=task_code, status='done')
    list_of_task_code = [task[3] for task in task_info]
    if task_code in list_of_task_code:
        text = ""
        for task in task_info:
            text += f"""
<b>Ish ID si:</b> <i>{task[0]}</i>
<b>Ish kodi:</b> <i>{task[3]}</i>
<b>Ish tavsifi:</b> <i>{task[2]}</i>\n
            """
        if len(task_info) > 1:
            await message.answer(
                text + "<b>{code} kodli ishdan qay birini o'chirmoqchisiz</b>".format(code=data['task_code']),
                reply_markup=(await task_delete_id_inline_button(state)),
                parse_mode=ParseMode.HTML)

        else:
            await message.answer(text + "<b>{code} kodli ish bitta ekan</b>".format(code=data['task_code']),
                                 reply_markup=(await task_delete_id_inline_button(state)),
                                 parse_mode=ParseMode.HTML)

    else:
        await message.answer("Kechirasiz bunday ID li  ish mavjud emas🤕", reply_markup=admin_task_edit_button())


@customer_router.callback_query(F.data == "➕Ish qo'shish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TaskAddForm.task_code)
    await callback.message.answer('Ishni kodini kiriting')


@customer_router.message(TaskAddForm.task_code)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(task_code=message.text)
    await state.set_state(TaskAddForm.photo)
    await message.answer('Ish suratini kiriting')


@customer_router.message(TaskAddForm.photo, F.photo)
async def description_handler(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.photo[-1].file_id)
    download_file = await message.bot.download_file(file.file_path)
    response = requests.post('https://telegra.ph/upload', files={'file': download_file})
    data = response.json()
    url = "https://telegra.ph" + data[0].get('src').replace(r"\\", '')
    await state.update_data(photo=url)
    await state.set_state(TaskAddForm.description)
    await message.answer('Ishning tavsifini kiriting')


@customer_router.message(TaskAddForm.description, ~F.text.startswith("/"))
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    Task(image=data['photo'], description=data['description'], task_code=data['task_code'], status='free').insert()
    await message.answer("Ish muvofaqiyatliy qo'shildi😊", reply_markup=admin_task_edit_button())


@customer_router.callback_query(F.data == "💱Ishni tahrirlash")
async def update_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetEditTaskCode.task_code)
    await callback.message.answer(text="<b>Tahrirlash uchun ishni kodini kiriting (Masalan: N-250)!</b>",
                                  parse_mode=ParseMode.HTML)
    return


@customer_router.message(GetEditTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
async def task_code_handler(message: Message, state: FSMContext):
    await state.update_data(task_code=message.text)
    data = await state.get_data()
    task_code = data['task_code']
    task_info = Task().select(task_code=task_code, status='free') + Task().select(task_code=task_code, status='done')
    text = ""
    if task_info:
        for task in list(task_info):
            text += (f"""
<b>ID:</b>  <i>{task[0]}</i>
<b>Ish kodi:</b>  <i>{task[3]}</i>
                """)
        await message.answer(text=text + """
<b>Tahrirlash uchun ishlardan birini ID sini bosing "
(Masalan: ID:1)!</b>
            """,
                             reply_markup=(await task_edit_id_inline_button(state)), parse_mode=ParseMode.HTML)
    else:
        await message.answer("Kechirasiz {code} ish kiritilmagan😔".format(code=task_code),
                             reply_markup=admin_task_edit_button())


@customer_router.callback_query(F.data.startswith("task_edit_", GetTaskIDForm.task_id))
async def detail_task_handler(callback: CallbackQuery, state: FSMContext):
    pk = callback.data.split("_")[-1]
    await state.update_data(task_id=pk)
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    status = ''
    if session_task[0][4] == 'free':
        status = "Bo'sh"
    elif session_task[0][4] == 'busy':
        status = 'Band qilingan'
    text = f"""
<b>ID:</b>  <i>{session_task[0][0]}</i>
<b>Tavsifi:</b>  <i>{session_task[0][2]}</i>
<b>Ish kodi:</b>  <i>{session_task[0][3]}</i>
<b>Ish holati:</b>  <i>{status}</i>
        """
    img = URLInputFile(url=session_task[0][1])
    await callback.message.delete()
    await callback.message.answer_photo(photo=img, caption=text, parse_mode=ParseMode.HTML)
    await state.set_state(TaskUpdateForm.task_code)
    await callback.message.answer(f"""
<b>Ish kodi:</b> <i>{session_task[0][3]}</i>
<b>Yangi Ish kodi kiriting✍</b>
    """, parse_mode=ParseMode.HTML)


@customer_router.message(TaskUpdateForm.task_code)
async def name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    await state.update_data(task_code=message.text)
    await state.set_state(TaskUpdateForm.description)
    await message.answer(f"""
<b>Tavsifi:</b> <i>{session_task[0][2]}</i>
<b>Yangi tavsifni kiriting✍</b>
        """, parse_mode=ParseMode.HTML)


@customer_router.message(TaskUpdateForm.description)
async def description_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    await state.update_data(description=message.text)
    await state.set_state(TaskUpdateForm.photo)
    img = URLInputFile(url=session_task[0][1])
    await message.answer_photo(photo=img, caption='Ishning eski surati 👆')
    await message.answer('Yangi suratni kiriting🖼')


@customer_router.message(TaskUpdateForm.photo, F.photo)
async def photo_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    file = await message.bot.get_file(message.photo[-1].file_id)
    download_file = await message.bot.download_file(file.file_path)
    response = requests.post('https://telegra.ph/upload', files={'file': download_file})
    data = response.json()
    url = "https://telegra.ph" + data[0].get('src').replace(r"\\", '')
    await state.update_data(photo=url)
    data = await state.get_data()
    Task().update_task_employee(task_code=data['task_code'], image=data['photo'], description=data['description'],
                                id=session_task[0][0])
    await message.answer("Muvafaqiyatliy o'zgartirildi😉", reply_markup=admin_task_edit_button())


@customer_router.callback_query(F.data == '↪Chiqish')
async def exit_callback(callback: CallbackQuery):
    await callback.message.delete()
