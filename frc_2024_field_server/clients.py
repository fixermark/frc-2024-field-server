from frc_2024_field_server.client import Client
from frc_2024_field_server.game.clients import new_client
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Message, Receiver
from dataclasses import dataclass
import logging
from telnetlib3 import TelnetReader, TelnetWriter

"""Collection of all clients and communicatoin tools to interact with them."""

logger = logging.getLogger(__name__)


@dataclass
class ClientMessage:
    alliance: Alliance
    field_element: FieldElement
    message: Message

class Clients(Receiver):
    def __init__(self):
        self.clients: list[list[Client|None]] = [[None,None],[None,None]]
        self._messages: list[ClientMessage] = []
        self.new_clients: list[Client] = []

    def connect(self, alliance: Alliance, element: FieldElement, client: Client) -> None:
        """Connect a client to the set of clients."""
        self.clients[alliance][element] = client

    async def new_connection_shell(self, reader: TelnetReader, writer: TelnetWriter) -> None:
        """Telnet-style shell handler for new clients."""

        inp = await reader.readline()
        if not inp:
            writer.write("NO\r\n")
            await writer.drain()
            return

        alliance, element = self._decode_field_element_id(inp)

        if alliance is None or element is None:
            logger.error("Unable to connect client with ID %s", inp)
            writer.write("NO\r\n")
            await writer.drain()
            return

        logger.info("Connected client %s %s", alliance.name, element.name)
        client = new_client(alliance, element, self)
        self.new_clients.append(client)
        self.clients[alliance][element] =client
        writer.write("OK\r\n")
        await writer.drain()
        await client.shell(reader, writer)

    def _decode_field_element_id(self, data: str) -> tuple[Alliance|None, FieldElement|None]:
        """Decodes the alliance and field element, or returns None,None if cannot decode."""
        if len(data) < 3 or data[0] != 'H':
            return None,None

        alliance: Alliance
        if data[1] == 'R':
            alliance = Alliance.RED
        elif data[1] == 'B':
            alliance = Alliance.BLUE
        else:
            return None,None

        field_element: FieldElement
        if data[2] == 'A':
            field_element = FieldElement.AMP
        elif data[2] == 'S':
            field_element = FieldElement.SPEAKER
        else:
            return None,None

        return alliance, field_element

    def get_messages(self) -> list[ClientMessage]:
        """Receives all queued messages."""
        msgs = self._messages
        self._messages = []
        return msgs

    def get_new_clients(self) -> list[Client]:
        """Get all new clients."""
        clients = self.new_clients
        self.new_clients = []
        return clients

    def receive_message(self, alliance: Alliance, element: FieldElement, message:Message):
        """Receive and enqueue a message."""
        self._messages.append(ClientMessage(alliance, element, message))

    async def output(self, alliance: Alliance, element: FieldElement, message: str) -> None:
        """Outputs a message to the specified client.

        Args:
          alliance: Which alliance to send message to.
          element: Which field element on that alliance to send message to.
          message: Message to send, *without* \\r\\n suffix.
        """

        client = self.clients[alliance][element]
        if client is None:
            logger.error("Unable to send %s to %s, %s: no client connected.", message, alliance, element)
            return

        await client.output(message)
