import asyncio
import logging
import time
from frc_2024_field_server.game.modes import Mode
from frc_2024_field_server.message_receiver import Alliance
from typing import Final

logger = logging.getLogger(__name__)

AUTON_PERIOD_NS: Final[int] = 15_000_000_000
TELEOP_PERIOD_NS: Final[int] = 135_000_000_000

"""State of game."""

class GameState:
    """State of the entire game."""

    def __init__(self):
        self.cur_time_ns:int = 0
        self.mode_end_ns:int = 0
        self.current_mode = Mode.SETUP
        self.alliances = (AllianceState(), AllianceState())

    def check_mode_progression(self) -> None:
        """Check if mode should progress and move it forward if it should."""
        next_mode: Mode | None = None

        if self.current_mode is Mode.AUTONOMOUS:
            next_mode = Mode.WAIT_FOR_TELEOP
        elif self.current_mode is Mode.TELEOP:
            next_mode = Mode.SETUP

        if next_mode is None:
            return

        if self.cur_time_ns > self.mode_end_ns:
            self.current_mode = next_mode
            self.mode_end_ns = 0

    def _start_round(self) -> None:
        """Initialize the round by zeroing out the scores and clearing state."""
        self.alliances[Alliance.RED].start_round()
        self.alliances[Alliance.BLUE].start_round()

    def handle_go_button(self) -> None:
        """Handle push of the explicit 'Go' button (space bar)."""
        current_ns = time.monotonic_ns()
        if self.current_mode is Mode.SETUP:
            self.current_mode = Mode.AUTONOMOUS
            self._start_round()
            self.mode_end_ns = current_ns + AUTON_PERIOD_NS
            return

        if self.current_mode is Mode.WAIT_FOR_TELEOP:
            self.current_mode = Mode.TELEOP
            self.mode_end_ns = current_ns + TELEOP_PERIOD_NS
            return

        # Override mid-match. Cancel match.
        self.current_mode = Mode.SETUP
        self.mode_end_ns = 0

    def get_remaining_time_ns(self) -> int:
        """If in a timed mode, get remaining time in nanos. Otherwise, get 0."""
        current_ns = time.monotonic_ns()
        if self.mode_end_ns == 0 or current_ns > self.mode_end_ns:
            return 0

        return self.mode_end_ns - current_ns

    def game_active(self) -> bool:
        """Return true if the game is in an active state (autonomous or teleop)."""
        return self.current_mode in [Mode.AUTONOMOUS, Mode.TELEOP]

class AllianceState:
    """State of a single alliance."""

    def __init__(self):
        self.score = 0
        self.amp_end_ns = 0  # if nonzero, time in match that the amp will wrap up.
        self.banked_notes = 0

    def start_round(self) -> None:
        """Init state for start of round."""
        self.score = 0
        self.amp_end_ns = 0
        self.banked_notes = 0

    def get_remaining_amp_time_ns(self, cur_time_ns: int) -> int:
        """Get remaining amp time, or 0 if amp is off."""
        return 0 if (self.amp_end_ns == 0 or self.amp_end_ns < cur_time_ns) else self.amp_end_ns - cur_time_ns
