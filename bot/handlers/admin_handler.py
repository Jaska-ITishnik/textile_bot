import requests
from aiogram import Router, F, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import set_my_commands
from aiogram.types import Message, CallbackQuery, URLInputFile

from bot.DTO.data_to_object import Employee, Task, User
from bot.bot_commands.all_commands import SUPER_ADMINS, on_startup
from bot.bot_functions.button_functions import admin_task_edit_button, \
    task_edit_id_inline_button, \
    admin_employee_edit_button, employee_edit_id_inline_button, adminka_back_button, admin_type, \
    task_delete_id_inline_button
from bot.states import TaskAddForm, EmployeeDeleteForm, EmployeeAddForm, GetEmployeeIdForm, \
    EmployeeUpdateForm, TaskUpdateForm
from bot.states.all_states import GetUserInfoForm, GetEditTaskCode, GetDeleteTaskCode, GetListTaskCode, \
    GetUserTelegramId

admin_router = Router()

admin_router.message.filter(F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(SUPER_ADMINS))


@admin_router.message(Command(commands=['ishchilar_royxati']))
async def add_handleer(message: Message):
    workers_info = Employee().select()
    text = ""
    status = ""
    for worker_info in list(workers_info):
        if worker_info[5] == 'free':
            status = "Bo'sh"
        elif worker_info[5] == 'in_process':
            status = 'Ishlayapti'
        elif worker_info[5] == 'finished':
            status = 'vazifa tugallangan'
        text += (f"""
<b>ID:</b>  <i>{worker_info[0]}</i>
<b>Ismi:</b>  <i>{worker_info[1]}</i>
        """)

    await message.answer(text=text, reply_markup=adminka_back_button(), parse_mode=ParseMode.HTML)


@admin_router.message(Command(commands=['ishlar_royxati']))
async def lis_of_task_handler(message: Message, state: FSMContext):
    await state.set_state(GetListTaskCode.task_code)
    await message.answer(text="""
<b>Ishlarni ko'rish uchun ish kodini kiriting!
Masalan(N-250)</b>

""",
                         parse_mode=ParseMode.HTML)


@admin_router.message(GetListTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
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


@admin_router.message(Command('ish_qoshish'))
async def add_task_button_handler(message: Message):
    await message.answer("Ish bo'limiga xush kelibsiz quyidagilardan qay birini tanlaysiz",
                         reply_markup=admin_task_edit_button())


@admin_router.callback_query(F.data == "❌Ishni o'chirish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetDeleteTaskCode.task_code)
    await callback.message.answer('<b>Ishni kodini kiriting🔢(Masalan: N-252)</b>', parse_mode=ParseMode.HTML)


@admin_router.message(GetDeleteTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
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


@admin_router.callback_query(F.data == "➕Ish qo'shish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TaskAddForm.task_code)
    await callback.message.answer('Ishni kodini kiriting')


@admin_router.message(TaskAddForm.task_code)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(task_code=message.text)
    await state.set_state(TaskAddForm.photo)
    await message.answer('Ish suratini kiriting')


@admin_router.message(TaskAddForm.photo, F.photo)
async def description_handler(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.photo[-1].file_id)
    download_file = await message.bot.download_file(file.file_path)
    response = requests.post('https://telegra.ph/upload', files={'file': download_file})
    data = response.json()
    url = "https://telegra.ph" + data[0].get('src').replace(r"\\", '')
    await state.update_data(photo=url)
    await state.set_state(TaskAddForm.description)
    await message.answer('Ishning tavsifini kiriting')


@admin_router.message(TaskAddForm.description, ~F.text.startswith("/"))
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    Task(image=data['photo'], description=data['description'], task_code=data['task_code'], status='free').insert()
    await message.answer("Ish muvofaqiyatliy qo'shildi😊", reply_markup=admin_task_edit_button())


@admin_router.callback_query(F.data == "💱Ishni tahrirlash")
async def update_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetEditTaskCode.task_code)
    await callback.message.answer(text="<b>Tahrirlash uchun ishni kodini kiriting (Masalan: N-250)!</b>",
                                  parse_mode=ParseMode.HTML)
    return


@admin_router.message(GetEditTaskCode.task_code, F.text.startswith('N-'), F.text.split('N-')[-1].isdigit())
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


#  ***********************************************************************************************************************************

@admin_router.message(Command('ishchi_qoshish'))
async def add_task_button_handler(message: Message):
    await message.answer("Ishchi bo'limiga xush kelibsiz quidagilardan qay birini tanlaysiz",
                         reply_markup=admin_employee_edit_button())


@admin_router.callback_query(F.data == "❌Ishchini o'chirish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EmployeeDeleteForm.pk)
    workers_info = Employee().select()
    text = ""
    for worker_info in list(workers_info):
        text += (f"""
<b>ID:</b>  <i>{worker_info[0]}</i>
<b>Ismi:</b>  <i>{worker_info[1]}</i>
<b>Familiyasi:</b>   <i>{worker_info[2]}</i>\n
            """)
    await callback.message.answer(text=text, parse_mode=ParseMode.HTML)

    await callback.message.answer("O'chirmoqchi bo'lgan ishchini ID sini kiriting")


@admin_router.message(EmployeeDeleteForm.pk, F.text.isdigit())
async def photo_handler(message: Message, state: FSMContext):
    await state.update_data(pk=message.text)
    data = await state.get_data()
    employee_info = Employee().select()
    if employee_info:
        list_of_employee_img = [employee[0] for employee in employee_info]
        if int(data['pk']) in list_of_employee_img:
            Employee().delete_employee(id=data['pk'])
            await message.answer("Muvofaqiyatliy o'chirildi🗑️", reply_markup=admin_employee_edit_button())
            return
        else:
            await message.answer("Kechirasiz bunday ID li ishchi mavjud emas🤕",
                                 reply_markup=admin_employee_edit_button())
    else:
        await message.answer("Hali bazada ishchilar mavjud emas😴")


@admin_router.callback_query(F.data == "➕Ishchi qo'shish")
async def add_task_rkb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EmployeeAddForm.position)
    await callback.message.answer('Ishchining kasbini kiriting👷')


@admin_router.message(EmployeeAddForm.position)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(EmployeeAddForm.first_name)
    await message.answer('Ishchining ismini kiriting✍')


@admin_router.message(EmployeeAddForm.first_name)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(EmployeeAddForm.last_name)
    await message.answer('Ishchining familiyasini kiriting✍')


@admin_router.message(EmployeeAddForm.last_name)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(EmployeeAddForm.telegram_id)
    await message.answer('Ishchining telegram ID sini kiriting🆔')


@admin_router.message(EmployeeAddForm.telegram_id, F.text.isdigit())
async def description_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(telegram_id=int(message.text))
    else:
        await message.answer("ID ni to'g'ri kiriting😬")
    data = await state.get_data()
    employee_info = Employee().select()
    list_of_employee_telegram_id = [employee[4] for employee in employee_info]
    if data['telegram_id'] not in list_of_employee_telegram_id:
        Employee(first_name=data['first_name'], last_name=data['last_name'], position=data['position'],
                 telegram_id=data['telegram_id'], status='free').insert()
        await message.answer("Ishchi muvofaqiyatliy qo'shildi😊", reply_markup=admin_employee_edit_button())
        return
    else:
        await message.answer("Bunday ishchi allaqachon mavjud🤨", reply_markup=admin_employee_edit_button())


@admin_router.callback_query(F.data == "💱Ishchini tahrirlash")
async def update_employee_rkb(callback: CallbackQuery, state: FSMContext):
    employee_info = Employee().select()
    text = ""
    for employee in list(employee_info):
        text += (f"""
<b>ID:</b>  <i>{employee[0]}</i>
<b>Ismi:</b>  <i>{employee[1]}</i>
<b>Familiyasi:</b>  <i>{employee[2]}</i>\n
            """)
    await state.set_state(GetEmployeeIdForm.employee_id)
    await callback.message.answer(text=text + "<b>To'liq ma'lumot uchun ID lardan birini tanlang!</b>",
                                  reply_markup=employee_edit_id_inline_button(), parse_mode=ParseMode.HTML)


@admin_router.callback_query(F.data.startswith("employee_edit_"), F.data.split("_")[-1].isdigit(),
                             GetEmployeeIdForm.employee_id)
async def detail_task_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(employee_id=callback.data.split("_")[-1])
    data = await state.get_data()
    session_employee_id = data['employee_id']
    session_employee_info = Employee().select(id=session_employee_id)
    status = ''
    if session_employee_info[0][5] == 'free':
        status = "Bo'sh"
    elif session_employee_info[0][5] == 'in_process':
        status = 'Bajarilmoqda'
    elif session_employee_info[0][5] == 'finished':
        status = 'Yakunlangan'
    text = f"""
<b>ID:</b>  <i>{session_employee_info[0][0]}</i>
<b>Telegram ID:</b>  <i>{session_employee_info[0][4]}</i>
<b>Ismi:</b>  <i>{session_employee_info[0][1]}</i>
<b>Familiyasi:</b>  <i>{session_employee_info[0][2]}</i>
<b>Ishchining holati:</b>  <i>{status}</i>
        """
    await callback.message.delete()
    await callback.message.answer(text=text, parse_mode=ParseMode.HTML)
    await state.set_state(EmployeeUpdateForm.first_name)
    await callback.message.answer(f"""
<b>Ismi(eski ma'lumot):</b> <i>{session_employee_info[0][1]}</i>
<b>Ismi(yangi ma'lumot)✍</b>
    """, parse_mode=ParseMode.HTML)


@admin_router.message(EmployeeUpdateForm.first_name)
async def name_handler(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(EmployeeUpdateForm.last_name)
    data = await state.get_data()
    session_employee_id = data['employee_id']
    session_employee_info = Employee().select(id=session_employee_id)
    await message.answer(f"""
<b>Familiyasi(eski ma'lumot):</b> <i>{session_employee_info[0][2]}</i>
<b>Familiyasi(yangi ma'lumot)✍</b>
        """, parse_mode=ParseMode.HTML)


@admin_router.message(EmployeeUpdateForm.last_name)
async def description_handler(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(EmployeeUpdateForm.position)
    data = await state.get_data()
    session_employee_id = data['employee_id']
    session_employee_info = Employee().select(id=session_employee_id)
    await message.answer(f"""
<b>Kasbi(eski ma'lumot): </b><i>{session_employee_info[0][3]}</i>
<b>Kasbi(yangi ma'lumot)✍</b>
                """, parse_mode=ParseMode.HTML)


@admin_router.message(EmployeeUpdateForm.position)
async def photo_handler(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(EmployeeUpdateForm.telegram_id)
    data = await state.get_data()
    session_employee_id = data['employee_id']
    session_employee_info = Employee().select(id=session_employee_id)
    await message.answer(f"""
<b>Telegram ID (eski ma'lumot): </b><i>{session_employee_info[0][4]}</i>
<b>Telegram ID (yangi ma'lumot)✍</b>
                            """, parse_mode=ParseMode.HTML)


@admin_router.message(EmployeeUpdateForm.telegram_id, F.text.isdigit())
async def photo_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(telegram_id=int(message.text))
        data = await state.get_data()
        session_employee_id = data['employee_id']
        session_employee_info = Employee().select(id=session_employee_id)
        Employee().update_task_employee(first_name=data['first_name'], last_name=data['last_name'],
                                        position=data['position'], telegram_id=data['telegram_id'],
                                        id=session_employee_info[0][0])
        await message.answer("Muvafaqiyatliy o'zgartirildi😉", reply_markup=admin_employee_edit_button())
    else:
        await message.answer("Telegram ID ni to'g'ri kiriting😬")


@admin_router.callback_query(F.data.startswith("task_edit_"))
async def detail_task_handler(callback: CallbackQuery, state: FSMContext):
    pk = callback.data.split("_")[-1]
    await state.update_data(task_id=int(pk))
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    status = ''
    if session_task[0][5] == 'free':
        status = "Bo'sh"
    elif session_task[0][5] == 'busy':
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


@admin_router.message(TaskUpdateForm.task_code)
async def name_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    await state.update_data(task_code=message.text)
    await state.set_state(TaskUpdateForm.description)
    await message.answer(f"""
<b>Tavsifi:</b> <i>{session_task[0][2]}</i>
<b>Yangi tavsifni kiriting✍</b>
        """, parse_mode=ParseMode.HTML)


@admin_router.message(TaskUpdateForm.description)
async def description_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session_task = Task().select(id=data['task_id'])
    await state.update_data(description=message.text)
    await state.set_state(TaskUpdateForm.photo)
    img = URLInputFile(url=session_task[0][1])
    await message.answer_photo(photo=img, caption='Ishning eski surati 👆')
    await message.answer('Yangi suratni kiriting🖼')


@admin_router.message(TaskUpdateForm.photo, F.photo)
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


@admin_router.callback_query(F.data == '↪Chiqish')
async def exit_callback(callback: CallbackQuery):
    await callback.message.delete()


@admin_router.callback_query(F.data.startswith('task_delete_'))
async def task_delete_callback(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('task_delete_')[-1])
    await callback.message.delete()
    Task().delete_task(pk=task_id)
    await callback.message.answer("Muvofaqiyatliy o'chirildi🗑️", reply_markup=admin_task_edit_button())
    return


@admin_router.callback_query(F.data.startswith("employee_detail_"))
async def detail_employee_handler(callback: CallbackQuery):
    pk = callback.data.split('_')[-1]
    session_user = Employee().select(id=int(pk))
    status = ''
    if session_user[0][5] == 'free':
        status = "Bo'sh"
    elif session_user[0][5] == 'in_process':
        status = 'Bajarilayapti'
    elif session_user[0][5] == 'finished':
        status = 'Tugallangan'
    if session_user[0][-1]:
        task_id = session_user[0][-1]
    else:
        task_id = 'Ish egallanmagan'

    employee_info = f"""
<b>ID:</b>  <i>{session_user[0][0]}</i>
<b>Ismi:</b>  <i>{session_user[0][1]}</i>
<b>Familiyasi:</b>  <i>{session_user[0][2]}</i>
<b>Lavozimi:</b>  <i>{session_user[0][3]}</i>
<b>Ish ID:</b>  <i>{task_id}</i>
<b>Ishchinig holati:</b>  <i>{status}</i>
    """
    await callback.message.answer(text=employee_info, reply_markup=adminka_back_button(), parse_mode=ParseMode.HTML)


@admin_router.message(Command('admin_qoshish'))
async def user_add_handler(message: Message, state: FSMContext):
    await state.set_state(GetUserInfoForm.first_name)
    await message.answer('Admin ismini kiriting✍')


@admin_router.message(GetUserInfoForm.first_name, F.text.isalpha)
async def first_name_handler(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(GetUserInfoForm.last_name)
    await message.answer('Admin familiyasini kiriting✍')


@admin_router.message(GetUserInfoForm.last_name, F.text.isalpha)
async def last_name_handler(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(GetUserInfoForm.type)
    await message.answer('Adminni turini tanlang kiriting✍', reply_markup=admin_type())


@admin_router.callback_query(GetUserInfoForm.type, F.data.endswith('_@'))
async def type_handler(callback: CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[0]
    await state.update_data(type=type)
    await state.set_state(GetUserInfoForm.telegram_id)
    await callback.message.answer('Admin telegram ID sini kiriting✍')


@admin_router.message(GetUserInfoForm.telegram_id, F.text.isdigit())
async def last_name_handler(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(telegram_id=int(message.text))
    data = await state.get_data()
    if data['type'] == "admin" or data['type'] == "moderator":
        User(first_name=data['first_name'],
             last_name=data['last_name'],
             type=data['type'],
             telegram_id=data['telegram_id']).insert()
        await message.answer("Admin muvofaqiyatliy qo'shildi☺")
    elif data['type'] == "monoblok":
        User(first_name=data['first_name'],
             type=data['type'],
             telegram_id=data['telegram_id']).insert()
        await message.answer("Monoblok muvofaqiyatliy qo'shildi☺")
    await on_startup(bot)


@admin_router.message(Command("admin_ochirish"))
async def admin_delete_handler(message: Message, state: FSMContext):
    await state.set_state(GetUserTelegramId.telegram_id)
    await message.answer("<b>O'chirish uchun adminni telegram ID sini kiriting🆔</b>", parse_mode=ParseMode.HTML)


@admin_router.message(GetUserTelegramId.telegram_id, F.text.isdigit())
async def admin_delete_handler(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(telegram_id=int(message.text))
    data = await state.get_data()
    telegram_id = data['telegram_id']
    User().delete_user(telegram_id=telegram_id)
    await message.answer("Admin muvofaqiyatliy o'chirildi😉")
    await on_startup(bot)

@admin_router.message(Command("adminlar_royxati"))
async def admin_delete_handler(message: Message):
    admin_infos = User().select()
    text = ""
    status = ""
    for admin_info in admin_infos:
        if admin_info[3] == 'admin':
            status = "🥇Admin"
        elif admin_info[3] == 'moderator':
            status = "🥈Buyurtmachi"
        elif admin_info[3] == 'monoblok':
            status = "🥉Monoblok"
        text += f"""
<b>ID</b>: <i>{admin_info[0]}</i> 
<b>Ismi</b>: <i>{admin_info[1]}</i> 
<b>Turi</b>: <i>{status}</i> 
<b>Telegram ID</b>: <i>{admin_info[4]}</i> 
        """
    await message.answer(text, reply_markup=adminka_back_button(), parse_mode=ParseMode.HTML)
