from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from redis import Redis

router = Router()


@router.message(Command("new_chat"))
async def new_chat(message: Message, redis: Redis) -> None:
    """/new_chat command. Deletes the chat thread for the user"""
    await redis.delete(f"chat_thread:{message.from_user.id}")
    await message.answer(text="New chat started!")
