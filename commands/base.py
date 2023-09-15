from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from control import ClientHandler

class Command (ABC):
    command_name = ""
    aliases = []

    def __init__(self, event, client_handler: 'ClientHandler'):
        self.event = event
        self.client_handler = client_handler

    @abstractmethod
    async def execute(self):
        pass

    async def parse_args(self, args):
        pass

    @classmethod
    def get_identifiers(cls):
        return [cls.command_name] + cls.aliases

# class Command:
#     command_name = ""
#     aliases = []
#
#     def __init__(self, event, client):
#         self.event = event
#         self.client = client
#
#     async def execute(self):
#         pass
#
#     async def parse_args(self, args):
#         pass
#
#     @classmethod
#     def register_with_manager(cls, manager):
#         manager.register_command(cls.command_name, cls, cls.aliases)