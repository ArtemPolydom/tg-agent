from aiogram import Router

from utils.openai import create_and_run

router = Router()


@router.message()
async def on_message(message, redis):
    await create_and_run(message, redis)
