# this bot is inteded to transcribe all voice and video messages sent by user, using telethon
import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')


import logging

logging.basicConfig(level=logging.INFO)

from commands import IngTranscribeCommand, IngGPTCommand

from control import ClientHandler

ruby_client = TelegramClient('ruby.session', api_key, api_hash)
ruby_commands = [IngTranscribeCommand, IngGPTCommand]
ruby_handler = ClientHandler(ruby_client, ruby_commands)

client = TelegramClient('session_name.session', api_key, api_hash)
client_commands = [IngTranscribeCommand, IngGPTCommand]
client_handler = ClientHandler(client, client_commands)


@ruby_client.on(events.NewMessage(incoming=False))
async def client2_event_listener(event):
    await ruby_handler.handle_event(event)

@client.on(events.NewMessage(incoming=False))
async def client1_event_listener(event):
    await client_handler.handle_event(event)


client.start()
ruby_client.start()
print("bot started")
client.run_until_disconnected()
