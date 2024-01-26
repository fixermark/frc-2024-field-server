from frc_2024_field_server.message_receiver import Message

"""Game-specific messages."""

class Score(Message):
    """Message indicating a point was scored."""

class AmpButtonPressed(Message):
    """Message indicating an Amp button was pressed."""

class CoopertitionButtonPressed(Message):
    """Message indicating a Coopertition button was pressed."""
