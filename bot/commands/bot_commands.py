from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot) -> None:
    """Setting bot commands"""

    data = [
        (
            [
                BotCommand(command="start", description="Start bot command"),  # Commands for private chats
                BotCommand(command="new_chat", description="Start new chat"),
            ],
            BotCommandScopeAllPrivateChats(),
            None
        ),
        (
            [
                BotCommand(command="hello", description="Say hello"),  # Commands for public chats

            ],
            None,
            None
        )
    ]

    for commands_list, commands_scope, language in data:
        await bot.set_my_commands(commands=commands_list, scope=commands_scope)
