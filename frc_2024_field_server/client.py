from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from enum import Enum, auto
import logging
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Receiver, Message
from telnetlib3 import TelnetReader,TelnetWriter
from typing import Literal

"""An individual client."""

class Datasource(Enum):
    """Enum indicating the source of data handled by the shell async process."""
    CLIENT_INPUT=auto()
    SERVER_OUTPUT=auto()

logger = logging.getLogger(__name__)

class ClientException(Exception):
    """An exception that occurs inside a client. Carries the client itself with it."""
    def __init__(self, client: Client):
        super().__init__(f"Exception raised from client [{client.alliance.name} | {client.field_element.name}]")
        self.client = client

class ClientClosedException(Exception):
    """An exception signalling a client closed."""


class Client(ABC):
    """An individual client connection."""

    def __init__(self, alliance: Alliance, element: FieldElement, receiver: Receiver):
        self.alliance = alliance
        self.field_element = element
        self.receiver = receiver
        self.output_queue = asyncio.Queue()

    async def shell(self, reader:TelnetReader, writer:TelnetWriter)-> None:
        """Processing shell for handling transactions between client and game."""
        try:
            await asyncio.gather(self.await_client_input_shell(reader),
                                self.await_server_output_shell(writer),
                                self.await_telnet_stream_monitor(reader, writer))
        except Exception as e:
            raise ClientException(self) from e

    async def await_client_input_shell(self, reader:TelnetReader) -> None:
        """Sub-task to await for client input."""
        while True:
            if reader.connection_closed:
                raise ClientClosedException()
            incoming: str = await reader.readline()
            self.handle_input(incoming)

    async def await_server_output_shell(self, writer: TelnetWriter) -> None:
        """Sub-task to await for server output."""
        while True:
            if writer.connection_closed:
                raise ClientClosedException()
            outgoing = await self.output_queue.get()
            writer.write(f'{outgoing}\r\n')

    async def await_telnet_stream_monitor(self, reader: TelnetReader, writer: TelnetWriter) -> None:
        """Active monitoring for connection closure.

        Necessary because connection closer doesn't un-wait readers and writers.
        """
        while True:
            if writer.connection_closed:
                raise ClientClosedException("Writer closed.")
            if reader.connection_closed:
                raise ClientClosedException("Reader closed.")

            await asyncio.sleep(0.5)


    async def output(self, msg: str) -> None:
        """Output a message to the connected client."""
        await self.output_queue.put(msg)

    @abstractmethod
    def handle_input(self, inp: str) -> None:
        """Handler for input coming from client."""

    @abstractmethod
    async def send_init_state(self, state: GameState) -> None:
        """Sends initial configuration to a newly-connected client."""

    def report_unknown_input(self, inp: bytes) -> None:
        """Utility function used by inheriting classes: reports unknown inputs."""
        logger.error("Unknown client input %s", inp)

    def send_message(self, message: Message) -> None:
        """Utility function used by inheriting classes. Send a message to my receiver."""
        self.receiver.receive_message(self.alliance, self.field_element, message)

