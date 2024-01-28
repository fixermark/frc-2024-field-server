"""Game modes"""

from enum import IntEnum

class Mode(IntEnum):
    SETUP = 0
    AUTONOMOUS = 1
    WAIT_FOR_TELEOP = 2
    TELEOP = 3
