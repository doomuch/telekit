from .base import Command


class IngGPTCommand(Command):
    command_name = "@ingGPT"
    aliases = ["@gpt"]

    async def execute(self):
        # Implementation
        ...
