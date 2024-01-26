
from abc import ABC, abstractmethod
import logging
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Receiver, Message

"""An individual client."""

logger = logging.getLogger(__name__)

class Client:
    """An individual client connection."""

    def __init__(self, alliance: Alliance, element: FieldElement, receiver: Receiver):
        self.alliance = alliance
        self.field_element = element
        self.receiver = receiver

    async def shell(self, reader, writer)-> None:
        """Processing shell for handling transactions between client and game."""
        # TODO: needs to await on both reader lines and outgoing game signal
        while True:
            inp = await reader.readline()
            if inp:
                self.handle_input(inp)

    def send_message(self, message: Message) -> None:
        """Send a message ot my receiver."""
        self.receiver.receive_message(self.alliance, self.field_element, message)


    def handle_input(self, inp: str) -> None:
        """Handler for input coming from client."""

    def report_unknown_input(self, inp: str) -> None:
        logger.error("Unknown client input %s", inp)

