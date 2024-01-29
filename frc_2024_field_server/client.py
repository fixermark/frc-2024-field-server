
from abc import ABC, abstractmethod
import asyncio
from enum import Enum, auto
import logging
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Receiver, Message
from telnetlib3 import TelnetReader,TelnetWriter
from typing import Literal

"""An individual client."""

class Datasource(Enum):
    """Enum indicating the source of data handled by the shell async process."""
    CLIENT_INPUT=auto()
    SERVER_OUTPUT=auto()

logger = logging.getLogger(__name__)

class Client(ABC):
    """An individual client connection."""

    def __init__(self, alliance: Alliance, element: FieldElement, receiver: Receiver):
        self.alliance = alliance
        self.field_element = element
        self.receiver = receiver
        self.output_queue = asyncio.Queue()

    async def shell(self, reader:TelnetReader, writer:TelnetWriter)-> None:
        """Processing shell for handling transactions between client and game."""
        await asyncio.wait([self.await_client_input_shell(reader),
                            self.await_server_output_shell(writer)])

    async def await_client_input_shell(self, reader:TelnetReader) -> None:
        """Sub-task to await for client input."""
        while True:
            incoming: str = await reader.readline()
            self.handle_input(incoming)

    async def await_server_output_shell(self, writer: TelnetWriter) -> None:
        """Sub-task to await for server output."""
        while True:
            outgoing = await self.output_queue.get()
            writer.write(f'{outgoing}\r\n')

    async def output(self, msg: str) -> None:
        """Output a message to the connected client."""
        await self.output_queue.put(msg)

    @abstractmethod
    def handle_input(self, inp: str) -> None:
        """Handler for input coming from client."""

    def report_unknown_input(self, inp: bytes) -> None:
        """Utility function used by inheriting classes: reports unknown inputs."""
        logger.error("Unknown client input %s", inp)

    def send_message(self, message: Message) -> None:
        """Utility function used by inheriting classes. Send a message to my receiver."""
        self.receiver.receive_message(self.alliance, self.field_element, message)

