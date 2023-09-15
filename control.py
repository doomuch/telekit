import os
from io import BytesIO

from telethon import TelegramClient, events
from telethon.errors import MessageTooLongError, MediaCaptionTooLongError, MessageNotModifiedError, \
    MessageDeleteForbiddenError

from commands import IngTranscribeCommand, IngGPTCommand
from utils import CustomMarkdown
from functools import wraps

import logging

logging.basicConfig(level=logging.INFO)


class CommandFactory:
    """
        Factory class responsible for creating command instances based on the provided command name.

        Methods:
        --------
        create_command(command_name, event, client, command_manager) -> Command:
            Returns a command instance for the given command name, or None if no matching command is found.
    """

    @staticmethod
    def create_command(command_name: str, event, client_handler: 'ClientHandler', command_manager: 'CommandManager'):
        command_class = command_manager.get_command(command_name)
        if command_class:
            return command_class(event, client_handler)
        return None


class EventAdapter:
    """
        Adapter class that provides a consistent interface for working with events.

        Attributes:
        -----------
        event: Event
            The original event object being wrapped.

        Methods:
        --------
        is_voice() -> bool:
            Determines if the event contains a voice message.

        get_message_text() -> str:
            Retrieves the text message from the event.
    """

    def __init__(self, event):
        self.event = event

    def is_voice(self):
        return self.event.message.voice

    def get_message_text(self):
        return self.event.message.message


class CommandManager:
    """
        Manager class that handles the registration and retrieval of command classes.

        Attributes:
        -----------
        _commands: dict
            Dictionary mapping command names to their corresponding classes.

        Methods:
        --------
        register_command(command_class):
            Registers a command class using its identifiers.

        register_commands(command_classes):
            Registers multiple command classes.

        get_command(command_name) -> CommandClass:
            Retrieves the command class for a given command name.
        """

    def __init__(self, commands=None):
        self._commands = {}
        if commands:
            self.register_commands(commands)

    def register_command(self, command_class):
        for identifier in command_class.get_identifiers():
            if identifier in self._commands:
                raise ValueError(f"Command with identifier {identifier} already registered!")
            self._commands[identifier] = command_class

    def register_commands(self, command_classes):
        for cmd_class in command_classes:
            self.register_command(cmd_class)

    def get_command(self, command_name):
        return self._commands.get(command_name)


class EventHandler:
    """
        Handler class that processes incoming events and executes the appropriate commands.

        Attributes:
        -----------
        client_handler: ClientHandler
            The client handler instance for sending messages.

        command_manager: CommandManager
            The command manager instance for retrieving command classes.

        Methods:
        --------
        handle(event):
            Handles the provided event by executing the relevant command.
    """

    def __init__(self, client_handler: 'ClientHandler'):
        self.client_handler = client_handler
        self.command_manager = CommandManager(client_handler.command_classes)

    async def handle(self, event):
        event_adapter = EventAdapter(event)
        command_name = EventHandler.get_command_name(event_adapter)
        if not command_name:
            return

        command = CommandFactory.create_command(command_name, event, self.client_handler, self.command_manager)
        if command:
            await command.execute()

    @staticmethod
    def get_command_name(event_adapter):
        if not isinstance(event_adapter, EventAdapter):
            raise TypeError(f"Expected an instance of EventAdapter, but got {type(event_adapter).__name__}.")

        if event_adapter.is_voice():
            return IngTranscribeCommand.command_name
        else:
            command_text = event_adapter.get_message_text()
            if not command_text:
                return None
            return command_text.split()[0]


class ClientHandler:
    """
        Handler class that encapsulates client-specific configurations and event handling logic.

        Attributes:
        -----------
        client: Client
            The client instance being managed.

        command_manager: CommandManager
            The command manager instance for the client.

        event_handler: EventHandler
            The event handler for processing client events.

        Methods:
        --------
        handle_event(event):
            Processes the given event using the client's event handler.

        download_voice(message, filepath, callback) -> str or None:
            Downloads the voice message from the given message and saves it to the specified filepath.
    """

    def __init__(self, client, command_classes):
        self.client = client
        client.parse_mode = CustomMarkdown()
        self.command_classes = command_classes
        self.event_handler = EventHandler(self)

    async def _register_event_handlers(self):
        @self.client.on(events.NewMessage(incoming=False))
        async def event_listener(event):
            await self.handle_event(event)

        logging.info("ClientHandler initialized.")

    async def start(self):
        await self._register_event_handlers()
        await self.client.start()
    async def handle_event(self, event):
        await self.event_handler.handle(event)

    async def download_media(self, message, file, progress_callback=None) -> str or None:
        return await self.client.download_media(message, file=file, progress_callback=progress_callback)

    async def send_text_as_file(self, peer_id, text, filename, reply_to=None):
        text_bytes = text.encode('utf-8')
        buffer = BytesIO(text_bytes)
        buffer.name = filename  # Add a name attribute to the BytesIO object
        buffer.seek(0)
        if reply_to:
            await self.client.send_file(peer_id, buffer, reply_to=reply_to)
        else:
            await self.client.send_file(peer_id, buffer)

    async def delete_message(self, peer_id, message_id):
        try:
            await self.client.delete_messages(peer_id, message_id)
        except MessageDeleteForbiddenError:
            logging.warning("Message delete forbidden")

    @staticmethod
    def emoji_parser(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            parse_mode = kwargs.get('parse_mode', None) or self.client.parse_mode
            kwargs['parse_mode'] = parse_mode
            return await func(self, *args, **kwargs)

        return wrapper

    @emoji_parser
    async def edit_message(self, peer_id, message_id, new_text, parse_mode=None, link_preview=None, file=None,
                           force_document=None):
        try:
            await self.client.edit_message(peer_id, message_id, new_text, link_preview=link_preview, file=file,
                                           force_document=force_document, parse_mode=parse_mode)
        except MediaCaptionTooLongError:
            await self.send_text_as_file(peer_id, new_text, "transcription.txt")
        except MessageNotModifiedError:
            logging.warning("Message not modified")

    @emoji_parser
    async def send_message(self, peer_id, message, parse_mode=None, link_preview=None, file=None, force_document=None):
        parse_mode = parse_mode or self.client.parse_mode

        if len(message) > 4096:
            await self.send_text_as_file(peer_id, message, "transcription.txt")
        else:
            await self.client.send_message(peer_id, message, parse_mode=parse_mode, link_preview=link_preview,
                                           file=file, force_document=force_document)

    @emoji_parser
    async def reply_message(self, peer_id, message, reply_to, parse_mode=None, link_preview=None, file=None,
                            force_document=None):
        if len(message) > 4096:
            await self.send_text_as_file(peer_id, message, "transcription.txt", reply_to=reply_to)
        else:
            await self.client.send_message(peer_id, message, reply_to=reply_to, parse_mode=parse_mode,
                                           link_preview=link_preview, file=file, force_document=force_document)

    async def get_message_by_id(self, peer_id, ids):
        return await self.client.get_messages(peer_id, ids=ids)

    async def download_voice(self, message, filepath, callback) -> str or None:
        if message.voice:
            filename = await self.client.download_media(message, file=filepath,
                                                        progress_callback=callback)

            return filename if filename else None


class ClientFactory():
    @staticmethod
    def create_client(client_data) -> 'ClientHandler':
        session_location_prefix = 'data/sessions/'
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        session_name = client_data.get("session_name")
        client = TelegramClient(session_location_prefix + session_name + ".session", api_id, api_hash)

        command_objects = [eval(command) for command in client_data['commands']]
        handler = ClientHandler(client, command_objects)

        return handler
