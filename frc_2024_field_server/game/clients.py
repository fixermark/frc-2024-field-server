from frc_2024_field_server.client import Client
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Receiver
from frc_2024_field_server.game.messages import Score, AmpButtonPressed, CoopertitionButtonPressed
"""Clients specific to the game."""

class UnknownClientException(Exception):
    """The specified client does not exist."""

class AmpClient(Client):
    def handle_input(self, inp: str) -> None:
        if inp[0] == "R":
            self.send_message(Score())
        elif inp[0] == "A":
            self.send_message(AmpButtonPressed())
        elif inp[0] == "C":
            self.send_message(CoopertitionButtonPressed())
        else:
            self.report_unknown_input(inp)

class SpeakerClient(Client):
    def handle_input(self, inp: str) -> None:
        if inp[0] == "R":
            self.send_message(Score())
        else:
            self.report_unknown_input(inp)


def new_client(alliance: Alliance, element: FieldElement, receiver: Receiver) -> Client:
    if element == FieldElement.AMP:
        return AmpClient(alliance, element ,receiver)
    elif element == FieldElement.SPEAKER:
        return SpeakerClient(alliance, element, receiver)
    else:
        raise UnknownClientException(f"No client for {element.name}")
