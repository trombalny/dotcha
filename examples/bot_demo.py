import os
import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from dotcha import CaptchaGenerator, Theme, Difficulty

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("Error: BOT_TOKEN environment variable not set.")
    TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()
generator = CaptchaGenerator(theme=Theme.LIGHT, difficulty=Difficulty.MEDIUM)

user_sessions: Dict[int, str] = {}
user_settings: Dict[int, Difficulty] = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Sends a new PNG captcha."""
    diff = user_settings.get(message.from_user.id, Difficulty.MEDIUM)
    gen = CaptchaGenerator(theme=Theme.LIGHT, difficulty=diff)
    
    captcha_text, image_bytes = await gen.agenerate()
    user_sessions[message.from_user.id] = captcha_text.upper()
    
    input_file = BufferedInputFile(image_bytes.getvalue(), filename="captcha.png")
    await message.answer_photo(
        photo=input_file,
        caption=f"Difficulty: {diff.value}\nPlease solve this captcha:"
    )

@dp.message(Command("gif"))
async def cmd_gif(message: types.Message):
    """Sends a new animated GIF captcha."""
    diff = user_settings.get(message.from_user.id, Difficulty.MEDIUM)
    gen = CaptchaGenerator(theme=Theme.LIGHT, difficulty=diff)
    
    await message.answer("Generating animation... ⏳")
    captcha_text, image_bytes = await gen.agenerate_gif(frames=10)
    user_sessions[message.from_user.id] = captcha_text.upper()
    
    input_file = BufferedInputFile(image_bytes.getvalue(), filename="captcha.gif")
    await message.answer_animation(
        animation=input_file,
        caption=f"🔥 Animated Captcha ({diff.value})\nLook at the movement to see the text!"
    )

@dp.message(Command("easy", "medium", "hard"))
async def cmd_difficulty(message: types.Message, command: Command):
    """Sets the difficulty level."""
    diff_map = {"easy": Difficulty.EASY, "medium": Difficulty.MEDIUM, "hard": Difficulty.HARD}
    new_diff = diff_map[command.command.lower()]
    user_settings[message.from_user.id] = new_diff
    await message.answer(f"✅ Difficulty set to: {new_diff.value}")

@dp.message(F.text)
async def handle_message(message: types.Message):
    """Checks the user's answer."""
    user_id = message.from_user.id
    expected = user_sessions.get(user_id)
    
    if not expected:
        await message.answer("Use /start to get a new captcha!")
        return
    
    user_answer = message.text.strip().upper()
    is_correct, distance = CaptchaGenerator.check_answer(user_answer, expected, fuzzy_tolerance=1)
    
    if is_correct:
        if distance == 0:
            await message.answer("✅ Perfect! You solved the captcha.")
        else:
            await message.answer(f"✅ Accepted! (Error was {distance} chars, but it's close enough).")
        del user_sessions[user_id]
    else:
        await message.answer(
            f"❌ Wrong answer. The correct code was: {expected}\n"
            f"Your distance: {distance} chars. Use /start or /gif for a new one."
        )
        del user_sessions[user_id]

async def main():
    print(f"Bot started. Using theme: {generator.schema}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
