from aiogram import Router
from .start import router as start_router


def register_user_commands(router: Router) -> None:
    router.include_router(start_router)
