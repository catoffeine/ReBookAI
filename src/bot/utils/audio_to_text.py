from aiogram import Bot


async def audio_to_text(bot: Bot, file_id) -> str:
    # конвертировать аудио в текст
    # bot передается для скачивания файла по file_id

    text = "конвертированный текст"
    return text