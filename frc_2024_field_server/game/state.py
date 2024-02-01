import asyncio
import logging
import time
from frc_2024_field_server.game.constants import AUTON_PERIOD_NS, TELEOP_PERIOD_NS, COOPERTITION_WINDOW_NS
from frc_2024_field_server.game.modes import Mode
from frc_2024_field_server.message_receiver import Alliance
from typing import Final

logger = logging.getLogger(__name__)


"""State of game."""

class GameState:
    """State of the entire game."""

    def __init__(self):
        self.cur_time_ns:int = 0
        self.prev_time_ns: int = 0
        self.mode_end_ns:int = 0
        self.current_mode = Mode.SETUP
        self.alliances = (AllianceState(), AllianceState())
        self.first_game_frame = False

    def check_mode_progression(self) -> bool:
        """Check if mode should progress and move it forward if it should.

        Return:
          True if we are at match end."""
        next_mode: Mode | None = None

        if self.current_mode is Mode.AUTONOMOUS:
            next_mode = Mode.WAIT_FOR_TELEOP
        elif self.current_mode is Mode.TELEOP:
            next_mode = Mode.SETUP

        if self.cur_time_ns > self.mode_end_ns and next_mode is not None:
            self.current_mode = next_mode
            self.mode_end_ns = 0

        return next_mode is Mode.SETUP

    def _start_round(self) -> None:
        """Initialize the round by zeroing out the scores and clearing state."""
        self.alliances[Alliance.RED].start_round()
        self.alliances[Alliance.BLUE].start_round()
        self.first_game_frame = True

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

    def get_remaining_time_ns(self, when=None) -> int:
        """If in a timed mode, get remaining time in nanos. Otherwise, get 0.

        If `when` is specified, compute off of that time instead of cur_time_ns.
        """

        if when is None:
            when = self.cur_time_ns

        if self.mode_end_ns == 0 or when > self.mode_end_ns:
            return 0

        return self.mode_end_ns - when

    def game_active(self) -> bool:
        """Return True if the game is in an active state (autonomous or teleop)."""
        return self.current_mode in [Mode.AUTONOMOUS, Mode.TELEOP]

    def coopertition_available(self, when=None) -> bool:
        """Return True if pressing the coopertition button is allowed at this time.

        If `when` is specified, compute off of that timestamp instead of cur_time_ns.
        """
        if not self.current_mode is Mode.TELEOP:
            return False

        time_remaining = self.get_remaining_time_ns(when)
        return time_remaining > TELEOP_PERIOD_NS - COOPERTITION_WINDOW_NS

class AllianceState:
    """State of a single alliance."""

    def __init__(self):
        self.score = 0
        self.amp_end_ns = 0  # if nonzero, time in match that the amp will wrap up.
        self.banked_notes = 0
        self.coopertition_offered = False

    def start_round(self) -> None:
        """Init state for start of round."""
        self.score = 0
        self.amp_end_ns = 0
        self.banked_notes = 0
        self.coopertition_offered = False

    def get_remaining_amp_time_ns(self, cur_time_ns: int) -> int:
        """Get remaining amp time, or 0 if amp is off."""
        return 0 if (self.amp_end_ns == 0 or self.amp_end_ns < cur_time_ns) else self.amp_end_ns - cur_time_ns
