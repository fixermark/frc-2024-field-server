import logging
import time

logger = logging.getLogger(__name__)

"""State of game."""

class GameState:
    """State of the entire game."""

    def __init__(self):
        self.initial_time_ns = 0

    async def game_loop(self) -> None:
        """The main loop of the game. Runs continuously until game is completed."""
        running = True
        self.initiial_time_ns = time.monotonic_ns()
        while running:
            cur_time_ns = time.monotonic_ns()
            cur_time_ms = (cur_time_ns - self.initial_time_ns) / 1e6

            if cur_time_ms > 120000:
                logger.info("Time up.")
                running = False



class AllianceState:
    """State of a single alliance."""

    def __init__(self):
        self.score = 0
        self.amp_end_ms = 0  # if nonzero, time in match that the amp will wrap up.

