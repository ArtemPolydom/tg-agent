from aiohttp import ClientSession

from bot.config import Config


async def save_lead_data(data: dict) -> str:
    """
    Function to save lead data
    """
    url = Config.PIPEDREAM_URL
    async with ClientSession() as session:
        async with session.post(url, json=data, ssl=False) as response:
            try:
                response.raise_for_status()
            except Exception as e:
                return f"Error saving lead data: {e}"

    return "Lead data saved successfully."
