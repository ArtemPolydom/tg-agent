from os import getenv


class Config:
    BOT_TOKEN = getenv('BOT_TOKEN')

    REDIS_HOST = getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = getenv('REDIS_PORT', 6379)
    REDIS_USER = getenv('REDIS_USER')
    REDIS_PASSWORD = getenv('REDIS_PASS')

    WEBHOOK_PATH = f'/bot/{BOT_TOKEN}'
    WEBHOOK_URL = getenv('WEBHOOK_URL') + WEBHOOK_PATH

    WEBAPP_HOST = '127.0.0.1'
    WEBAPP_PORT = int(getenv('WEBAPP_PORT', '80'))

    OPENAI_API_KEY = getenv("OPENAI_API_KEY")
    ASSISTANT_ID = getenv("ASSISTANT_ID")
    PIPEDREAM_URL = getenv("PIPEDREAM_URL")
