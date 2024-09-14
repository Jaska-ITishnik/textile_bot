from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from bot.DTO.data_to_object import User

RESPONSIBLE_ADMIN = User().select('telegram_id', type='admin', id=3)[0][0]
SIMPLE_ADMINS = []
SUPER_ADMINS = []
MONOBLOCKS = []
for telegram_id in User().select('telegram_id', type='admin'):
    SUPER_ADMINS.append(telegram_id[0])

for telegram_id in User().select('telegram_id', type='moderator'):
    SIMPLE_ADMINS.append(telegram_id[0])

for telegram_id in User().select('telegram_id', type='monoblok'):
    MONOBLOCKS.append(telegram_id[0])


async def on_startup(bot: Bot):
    for monoblock in MONOBLOCKS:
        monoblocks_command = [
            BotCommand(command='start', description="Botni ishga tushirish"),
        ]
        await bot.set_my_commands(monoblocks_command, BotCommandScopeChat(chat_id=monoblock))

    for super_admin in SUPER_ADMINS:
        super_admins_command = [
            BotCommand(command='start', description="Botni ishga tushirish"),
            BotCommand(command="ish_qoshish", description="Yangi ish qo'shish"),
            BotCommand(command="ishchi_qoshish", description="Yangi ishchini qo'shish"),
            BotCommand(command='ishchilar_royxati', description="Ishchilar ro'yxatini olish"),
            BotCommand(command='ishlar_royxati', description="Ishlar ro'yxatini olish"),
            BotCommand(command="admin_qoshish", description="Yangi adminni qo'shish"),
            BotCommand(command="admin_ochirish", description="Adminni o'chirish"),
            BotCommand(command="adminlar_royxati", description="Adminlarni ro'yxatini ko'rish"),
        ]
        await bot.set_my_commands(super_admins_command, BotCommandScopeChat(chat_id=super_admin))

    for simple_admin in SIMPLE_ADMINS:
        simple_admins_command = [
            BotCommand(command='start', description="Botni ishga tushirish"),
            BotCommand(command="ish_qoshish", description="Yangi ish qo'shish"),
            BotCommand(command='ishlar_royxati', description="Ishlar ro'yxatini olish"),
        ]
        await bot.set_my_commands(simple_admins_command, BotCommandScopeChat(chat_id=simple_admin))


async def on_shutdown(bot: Bot):
    await bot.delete_my_commands()


# async def on_startup(bot: Bot):
#     for monoblock in MONOBLOCKS:
#         monoblocks_command = [
#
#             BotCommand(command='start', description="Botni ishga tushirish"),
#
#         ]
#
#         await bot.set_my_commands(monoblocks_command, BotCommandScopeChat(chat_id=monoblock))
#
#     for super_admin in SUPER_ADMINS:
#         super_admins_command = [
#
#             BotCommand(command='start', description="Botni ishga tushirish"),
#             BotCommand(command="ish_qoshish", description="Yangi ish qo'shish"),
#             BotCommand(command="ishchi_qoshish", description="Yangi ishchini qo'shish"),
#             BotCommand(command='ishchilar_royxati', description="Ishchilar ro'yxatini olish"),
#             BotCommand(command='ishlar_royxati', description="Ishlar ro'yxatini olish"),
#             BotCommand(command="admin_qoshish", description="Yangi adminni qo'shish"),
#             BotCommand(command="admin_ochirish", description="Adminni o'chirish"),
#             BotCommand(command="adminlar_royxati", description="Adminlarni ro'yxatini ko'rish")
#
#         ]
#         await bot.set_my_commands(super_admins_command, BotCommandScopeChat(chat_id=super_admin))
#     for simple_admin in SIMPLE_ADMINS:
#         simple_admins_command = [
#
#             BotCommand(command='start', description="Botni ishga tushirish"),
#             BotCommand(command="ish_qoshish", description="Yangi ish qo'shish"),
#             BotCommand(command='ishlar_royxati', description="Ishlar ro'yxatini olish")
#
#         ]
#         await bot.set_my_commands(simple_admins_command, BotCommandScopeChat(chat_id=simple_admin))

