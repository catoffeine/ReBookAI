import os

from aiogram import Bot
from pydub import AudioSegment
import speech_recognition as sr

from bot import errors


async def audio_to_text(bot: Bot, file_id: str) -> str:
    """
    Асинхронно обрабатывает голосовое сообщение и возвращает распознанный текст.
    :param bot: Экземпляр бота.
    :param file_id: ID файла в Telegram.
    :return: Распознанный текст.
    """

    # Создаем пути для временных файлов
    ogg_file_path = f"temp/{file_id}.ogg"
    wav_file_path = f"temp/{file_id}.wav"

    if not os.path.exists("temp"):
        os.mkdir("temp")

    try:
        # Скачиваем голосовое сообщение
        await bot.download(file_id, destination=ogg_file_path)

        # Конвертируем OGG в WAV
        AudioSegment.from_ogg(ogg_file_path).export(wav_file_path, format="wav")

        # Транскрибируем аудио
        recognizer = sr.Recognizer()

        def recognize():
            with sr.AudioFile(wav_file_path) as source:
                audio_data = recognizer.record(source)
                try:
                    return recognizer.recognize_google(audio_data, language="ru-RU")
                except sr.UnknownValueError:
                    raise errors.EmptyVoiceError
                except sr.RequestError as e:
                    raise errors.VoiceRecognitionError

        text = recognize()
        return text

    finally:
        # Удаляем временные файлы
        for temp_file in [ogg_file_path, wav_file_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)