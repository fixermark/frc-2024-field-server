from typing import Final
from frc_2024_field_server.game.modes import Mode

"""Relevant constants for game rules."""

# Note: notes have scores in waiting modes to account for late rings (3-second rule)
AMP_NOTE_SCORE_FOR_MODE: Final = {
    Mode.AUTONOMOUS: 2,
    Mode.SETUP: 1,
    Mode.WAIT_FOR_TELEOP: 2,
    Mode.TELEOP: 1,
}

# Note: notes have scores in waiting modes to account for late rings (3-second rule)
UNAMPLIFIED_SPEAKER_NOTE_SCORE_FOR_MODE: Final = {
    Mode.AUTONOMOUS: 5,
    Mode.TELEOP: 2,
    Mode.WAIT_FOR_TELEOP: 5,
    Mode.SETUP: 2,
}

AMPLIFIED_SPEAKER_NOTE_SCORE: Final = 5

