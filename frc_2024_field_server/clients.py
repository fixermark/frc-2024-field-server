from frc_2024_field_server.client import Client
from frc_2024_field_server.game.clients import new_client
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Message, Receiver
from dataclasses import dataclass
import logging

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

    def connect(self, alliance: Alliance, element: FieldElement, client: Client) -> None:
        """Connect a client to the set of clients."""
        self.clients[alliance][element] = client

    async def new_connection_shell(self, reader, writer) -> None:
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
        self.clients[alliance][element] =client
        writer.write("OK\r\n")
        await writer.drain()
        await client.shell(reader, writer)

    def _decode_field_element_id(self, data: str) -> tuple[Alliance|None, FieldElement|None]:
        """Decodes the alliance and field element, or returns None,None if cannot decode."""
        if len(data) < 2:
            return None,None

        alliance: Alliance
        if data[0] == 'R':
            alliance = Alliance.RED
        elif data[0] == 'B':
            alliance = Alliance.BLUE
        else:
            return None,None

        field_element: FieldElement
        if data[1] == 'A':
            field_element = FieldElement.AMP
        elif data[1] == 'S':
            field_element = FieldElement.SPEAKER
        else:
            return None,None

        return alliance, field_element

    def get_messages(self) -> list[ClientMessage]:
        """Receives all queued messages."""
        msgs = self._messages
        self._messages = []
        return msgs


    def receive_message(self, alliance: Alliance, element: FieldElement, message:Message):
        """Receive and enqueue a message."""
        self._messages.append(ClientMessage(alliance, element, message))
