import datetime
import json
from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile
from redis_dict import RedisDict

from bot.DTO.data_to_object import Employee, Task
from bot.bot_commands.all_commands import SUPER_ADMINS, MONOBLOCKS, RESPONSIBLE_ADMIN
from bot.bot_functions.button_functions import bot_futter_buttons, task_show, choose_task_inline_buttons, \
    employee_confirmation, \
    employee_empty_task_back, admin_confirmation
from bot.states import GetTaskIDForm, GetTelegramIDForm

user_router = Router()

user_router.message.filter(F.chat.type == ChatType.PRIVATE)

database = RedisDict()


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(text=f'Asssalomu aleykum <b>{message.from_user.full_name}</b>!\nXush kelibsiz!',
                         reply_markup=bot_futter_buttons(), parse_mode=ParseMode.HTML)


@user_router.message(F.text == "👷 Ish olish")
async def kitoblar_handler(message: Message, state: FSMContext):
    task_ids = Task().select('id', status='free')
    if message.from_user.id in SUPER_ADMINS or message.from_user.id in MONOBLOCKS:
        if task_ids:
            await state.set_state(GetTaskIDForm.task_id)
            await message.answer(text='Siz uchun maxsus vazifangizni olishingiz mumkin☺:',
                                 reply_markup=choose_task_inline_buttons(state).as_markup())
        else:
            await message.answer("Hamma vazifalar band qilingan🧐", reply_markup=employee_empty_task_back())
    else:
        await message.answer("Ish tanlash uchun adminga murojat qiling🤝", reply_markup=bot_futter_buttons())


@user_router.callback_query(F.data.startswith("task_choose_"))
async def book_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(task_id=callback.data.split("_")[-1])
    employees = Employee().select(status='free')
    if employees:
        text = ""
        for employee in list(employees):
            text += (f"""
<b>ID</b>: <i>{employee[0]}</i>
<b>Ismi</b>: <i>{employee[1]}</i>
<b>Familiyasi</b>: <i>{employee[2]}</i>
                    """)

        await state.set_state(GetTelegramIDForm.telegram_id)
        await callback.message.answer(text=text, parse_mode=ParseMode.HTML)
        await callback.message.answer(text="<b>🔍 ID ingizni kiriting🆔</b>", parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer(text="Hozirda barcha ishchilar band 😉", reply_markup=bot_futter_buttons())
        return


@user_router.message(GetTelegramIDForm.telegram_id, F.text.isdigit())
async def telegram_id_handler(message: Message, state: FSMContext):
    await state.update_data(employee_id=message.text)
    data = await state.get_data()
    employee_id = int(data['employee_id'])
    task_id = data['task_id']
    employee_id_list = []
    for employee in Employee().select():
        employee_id_list.append(employee[0])
    if employee_id in employee_id_list:
        session_employee = Employee().select(id=employee_id)
        session_employee_telegram_id = session_employee[0][4]
        description = (await task_show(state, task_id, session_employee_telegram_id))[2]
        ikb = (await task_show(state, task_id, session_employee_telegram_id))[0]
        if Employee().select(telegram_id=session_employee_telegram_id)[0][5] == 'free':
            await message.answer_photo(photo=(await task_show(state, task_id, session_employee_telegram_id))[1],
                                       caption=description,
                                       reply_markup=ikb, parse_mode=ParseMode.HTML)
        else:
            await message.answer('Kechirasiz siz ishni yakunlaganingizdan keyin olish imkoniga egasiz🤕',
                                 reply_markup=bot_futter_buttons())
    else:
        await message.answer("Bunday ID li ishchi yo'q😔")


@user_router.callback_query(F.data == "back")
async def back_to_category_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()


@user_router.callback_query(F.data.startswith("employee_task_choose"))
async def employee_choose_handler(callback: CallbackQuery):
    task_id = callback.data.split('_')[-2]
    employee_telegram_id = callback.data.split('_')[-1]
    employee_info = Employee().select(telegram_id=employee_telegram_id)
    task_info = Task().select(id=task_id)
    announce_to_employee = f"""
<b>Ish tavsifi:</b> <i>{task_info[0][2]}</i>
<b>Ish kodi:</b> <i>{task_info[0][3]}</i>
<b>Ishni kim olgan:</b> <i>{employee_info[0][1]} {employee_info[0][2]}</i>
<b>Olingan vaqti:</b> <i>{str(datetime.now().time()).split('.')[0]}</i>
    """
    # if task_info[0][1]:
    #     img = URLInputFile(url=task_info[0][1])
    # else:
    #     img = URLInputFile(url='https://telegra.ph/file/acd0ab0de7bbb50bdf304.png')
    await callback.message.edit_caption(caption=f'{announce_to_employee}', parse_mode=ParseMode.HTML)
    await callback.message.bot.send_photo(chat_id=employee_telegram_id, photo=task_info[0][1],
                                          caption=announce_to_employee,
                                          reply_markup=employee_confirmation(employee_telegram_id),
                                          parse_mode=ParseMode.HTML)
    Task().update_task_employee(status='busy', id=task_id)
    Employee().update_task_employee(status='in_process', task_id=task_id, telegram_id=employee_telegram_id)
    await callback.message.answer(text="Ish muvofaqqiyatliy tanlandi😊", reply_markup=bot_futter_buttons())


@user_router.callback_query(F.data == 'empty_task_back')
async def back_to_choose(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Iltimos vazifa kelishini kuting⌛', reply_markup=bot_futter_buttons())


@user_router.callback_query(F.data.startswith('employee_finished_task_'))
async def admin_confirmation_handler(callback: CallbackQuery):
    text = callback.message.caption
    if 'Ishchi tel ID' not in text:
        text += "\n" + f"Ishchi tel ID: {callback.from_user.id}"
    database['current_employee'] = callback.from_user.model_dump_json()
    current_employee = json.loads(database['current_employee'])
    task_id = Employee().select('task_id', telegram_id=current_employee['id'])[0][0]
    # img = URLInputFile(url=Task().select(id=task_id)[0][1])
    img = Task().select(id=task_id)[0][1]
    await callback.message.bot.send_photo(chat_id=RESPONSIBLE_ADMIN, caption=text, photo=img,
                                          reply_markup=admin_confirmation())
    await callback.message.delete()
    await callback.message.answer(text="<b>{first_name}</b> sizning ishingiz adminga yuborildi☺".format(
        first_name=f"{current_employee['first_name']}"), parse_mode=ParseMode.HTML)


@user_router.callback_query(F.data.in_({"admin_confirm", "admin_ignore"}))
async def admin_desicion_handler(callback: CallbackQuery):
    text = callback.message.caption
    task_id = Employee().select('task_id', telegram_id=int(text.split()[-1]))[0][0]
    task_info = Task().select(id=task_id)
    if callback.data == 'admin_confirm':
        Task().update_task_employee(status="done", id=task_id)
        Employee().update_task_employee(status='finished', telegram_id=int(text.split()[-1]))
        infos_for_admin = Employee().select('first_name', 'last_name', 'status', telegram_id=int(text.split()[-1]))
        employee_first_name = infos_for_admin[0][0]
        employee_last_name = infos_for_admin[0][1]
        employee_status = infos_for_admin[0][2]
        if employee_status == 'finished':
            await callback.message.bot.send_message(chat_id=RESPONSIBLE_ADMIN,
                                                    text=f"""
<b>Vazifani bajardi✅: </b><i>{employee_first_name} {employee_last_name}</i>
<b>Ishchining telegram ID si: </b><i>{int(text.split()[-1])}</i>
<b>Vazifa tavsifi: </b> <i>{task_info[0][2]}</i>
<b>Ishning kodi: </b> <i>{task_info[0][3]}</i>
<b>Tugagan vaqti: </b> <i>{str(datetime.now().time()).split('.')[0]}</i>
                                        """, parse_mode=ParseMode.HTML)

        Employee().update_task_employee(status="free", task_id=None, telegram_id=int(text.split()[-1]))
        await callback.message.bot.send_message(chat_id=int(text.split()[-1]),
                                                text="Sizning ishingiz tasdiqlandi✅",
                                                parse_mode=ParseMode.HTML)
        await callback.message.bot.send_message(chat_id=int(text.split()[-1]),
                                                text=f"""
<b>Vazifani bajardi✅: </b><i>{employee_first_name} {employee_last_name}</i>
<b>Ishchining telegram ID si: </b><i>{int(text.split()[-1])}</i>
<b>Vazifa tavsifi: </b> <i>{task_info[0][2]}</i>
<b>Ishning kodi: </b> <i>{task_info[0][3]}</i> 
<b>Tugagan vaqti: </b> <i>{str(datetime.now().time()).split('.')[0]}</i>
                                                            """, parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == 'admin_ignore':
        task_photo = Task().select(id=task_id)[0][1]
        # img = URLInputFile(url=task_photo)
        await callback.message.delete()
        await callback.message.bot.send_photo(chat_id=int(text.split()[-1]),
                                              caption=text, photo=task_photo,
                                              reply_markup=employee_confirmation(int(text.split()[-1])))
        await callback.message.bot.send_message(chat_id=int(text.split()[-1]),
                                                text="Sizning ishingiz tasdiqlanmadi!🤕",
                                                parse_mode=ParseMode.HTML)
