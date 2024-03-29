from aiogram import Router
from aiogram.types import Message
from redis import Redis

from bot.chat.service import ChatService

router = Router()


@router.message()
async def on_message(message: Message, redis: Redis):
    """Handle incoming  from users"""
    await ChatService.handle_message(message, redis)
