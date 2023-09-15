import math
import os

from pydub import AudioSegment


class AudioHelper:
    @staticmethod
    async def convert_media_to_mp3(file_path):
        input_format = os.path.splitext(file_path)[1][1:]
        output_path = os.path.splitext(file_path)[0] + '.mp3'
        AudioSegment.from_file(file_path, input_format).export(output_path, format='mp3')
        return output_path

    @staticmethod
    async def get_size_mb(file_path):
        size_in_bytes = os.path.getsize(file_path)
        size_in_mb = size_in_bytes / (1024 * 1024)
        return size_in_mb

    @staticmethod
    def split_audio(file_path, max_size=2) -> list[AudioSegment]:
        audio = AudioSegment.from_mp3(file_path)

        duration = len(audio)
        fragment_duration = math.ceil(
            (max_size * 1000 * 1024 * 1024) / audio.frame_rate / audio.sample_width / audio.channels)
        fragments = []
        start = 0

        while start < duration:
            end = min(start + fragment_duration, duration)
            fragments.append(audio[start:end])
            start = end

        return fragments


from telethon.extensions import markdown
from telethon import types


class CustomMarkdown:
    @staticmethod
    def parse(text):
        text, entities = markdown.parse(text)
        for i, e in enumerate(entities):
            if isinstance(e, types.MessageEntityTextUrl):
                if e.url == 'spoiler':
                    entities[i] = types.MessageEntitySpoiler(e.offset, e.length)
                elif e.url.startswith('emoji/'):
                    entities[i] = types.MessageEntityCustomEmoji(e.offset, e.length, int(e.url.split('/')[1]))
        return text, entities

    @staticmethod
    def unparse(text, entities):
        for i, e in enumerate(entities or []):
            if isinstance(e, types.MessageEntityCustomEmoji):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, f'emoji/{e.document_id}')
            if isinstance(e, types.MessageEntitySpoiler):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, 'spoiler')
        return markdown.unparse(text, entities)
