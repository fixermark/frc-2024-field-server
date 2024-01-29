from dataclasses import dataclass
from frc_2024_field_server.message_receiver import FieldElement, Message

"""Game-specific messages."""

@dataclass
class Score(Message):
    """Message indicating a point was scored."""
    element: FieldElement

@dataclass
class AmpButtonPressed(Message):
    """Message indicating an Amp button was pressed."""

@dataclass
class CoopertitionButtonPressed(Message):
    """Message indicating a Coopertition button was pressed."""
