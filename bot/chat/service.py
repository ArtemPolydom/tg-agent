import asyncio
import json
import logging
import openai
from aiogram.types import Message
from openai.types.beta.threads import TextContentBlock
from redis import Redis
from bot.config import Config
from bot.chat.leads_api import save_lead_data


class ChatService:
    @staticmethod
    async def create_chat_thread() -> str | None:
        """Creates a new chat thread ID"""
        try:
            thread = openai.beta.threads.create()
            return thread.id
        except openai.OpenAIError as e:
            logging.error(f"OpenAI Error creating chat thread: {e}")
            return None

    @staticmethod
    async def add_message_to_thread(thread_id: str, message: Message) -> None:
        """Adds a user message to the thread and returns the model ID"""
        message_data = {"role": "user", "content": message.text}
        openai.beta.threads.messages.create(thread_id=thread_id, **message_data)

    @staticmethod
    async def handle_message(message: Message, redis: Redis):
        """
        Retrieves or creates a chat thread for the user, adds the message,
        and initiates a run with the Assistant.
        """
        user_id = message.from_user.id  # Assuming unique user ID
        thread_id = await redis.get(f"chat_thread:{user_id}")
        if not thread_id:
            thread_id = await ChatService.create_chat_thread()
            if not thread_id:
                await message.answer("Error creating chat thread. Try again later.")
                return
            await redis.set(f"chat_thread:{user_id}", thread_id)
        await ChatService.add_message_to_thread(thread_id, message)
        try:
            await ChatService.create_assistant_run(message, thread_id)
        except openai.OpenAIError as e:
            logging.error(f"OpenAI Error: {e}")
            await message.answer("Error. Try again later.")

    @staticmethod
    async def create_assistant_run(message: Message, thread_id):
        """Encapsulates run creation and monitoring"""
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=Config.ASSISTANT_ID
        )
        run = await ChatService.monitor_run_status(run, message, thread_id)
        if run.status == "completed":
            # Add logic to retrieve and send Assistant response
            gpt_messages = openai.beta.threads.messages.list(thread_id=thread_id).data
            last_mes_content: TextContentBlock = gpt_messages[0].content[0]
            await message.answer(str(last_mes_content.text.value))
        else:
            logging.error(f"Run failed with status: {run.status}")
            await message.answer("Error. Try again later")
        return run

    @staticmethod
    async def monitor_run_status(run, message, thread_id):
        """Monitors the run status and handles required actions."""
        while run.status in ["queued", "requires_action", "in_progress", "cancelling"]:
            await asyncio.sleep(1)  # Optional delay
            run = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == "requires_action":
                await ChatService.handle_required_action(run, message, thread_id)
        return run

    @staticmethod
    async def handle_required_action(run, message, thread_id):
        """Handles the required action for the run."""
        await message.answer("Function triggered...")
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = [await ChatService.get_output_for_tool_call(tool_call) for tool_call in tool_calls]
        openai.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    @staticmethod
    async def get_output_for_tool_call(tool_call):
        """Get the output for a tool call."""
        if tool_call.function.name == "save_lead_data":
            lead_data = json.loads(tool_call.function.arguments)
            output = await ChatService.handle_save_lead_data(lead_data)
        else:
            output = "Incorrect function name."
        return {
            'tool_call_id': tool_call.id,
            'output': output,
        }

    @staticmethod
    async def handle_save_lead_data(lead_data):
        """Handle the save_lead_data tool call."""
        if not all(lead_data.values()):
            missing_data = ", ".join(key for key, value in lead_data.items() if not value)
            return f"Not enough data provided. Missing: {missing_data}"
        try:
            return await save_lead_data(lead_data)
        except Exception as e:
            logging.error(f"Error saving lead data: {e}")
            return f"Error saving lead data: {e}"
