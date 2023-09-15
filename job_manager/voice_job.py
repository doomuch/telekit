from .job import BaseJob
from utils import AudioHelper
import openai
from job_manager.transcription_result import TranscriptionResult

import logging
logger = logging.getLogger(__name__)



class VoiceJob(BaseJob):
    SIZE_LIMIT = 20

    def __init__(self, client_handler, message):
        super().__init__(client_handler, message)
        self._job_directory = self._create_job_directory()
        self._prompt = ""
        self._client_handler = client_handler

    def get_file_path(self):
        return self._job_directory + "/" + self._id + ".ogg"

    async def process_job(self) -> TranscriptionResult:
        downloaded_media_path = await self.manage_download()
        converted_media_path = await AudioHelper.convert_media_to_mp3(downloaded_media_path)

        size = await AudioHelper.get_size_mb(converted_media_path)

        result = None
        if size > self.SIZE_LIMIT:
            logger.info(f"Audio file is too large ({size} MB), splitting into smaller segments")
            audio_segments = AudioHelper.split_audio(converted_media_path)
            for audio_segment in audio_segments:
                verbose_answer = await openai.Audio.atranscribe("whisper-1", audio_segment, response_format="verbose_json",
                                                                prompt=self._prompt)
                if result is None:
                    result = TranscriptionResult(verbose_answer)
                else:
                    result.add_verbose_answer(verbose_answer)

            print(result.get_json())

        else:
            result = await self.transcribe()

        return result

    async def manage_download(self):
        if not self._message.voice:
            raise TypeError("Message is not a voice message")

        filename = self._id + ".ogg"
        client = self._client_handler

        return await client.download_media(self._message, file=self._job_directory + "/" + filename)

    async def transcribe(self) -> TranscriptionResult:

        with open(self.get_file_path(), 'rb') as file:
            verbose_answer = await openai.Audio.atranscribe("whisper-1", file, response_format="verbose_json",
                                                            prompt=self._prompt)

        result = TranscriptionResult(verbose_answer)

        return result
