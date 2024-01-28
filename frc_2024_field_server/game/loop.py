from typing import Final

import asyncio
import logging
import time
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.clients import Clients, ClientMessage

"""The main game loop."""

logger = logging.getLogger(__name__)

MAIN_PERIOD_MSEC: Final = 50

def process_messages(state: GameState, clients: Clients, msgs: list[ClientMessage]) -> None:
    """Process incoming messages."""
    for msg in msgs:
        logger.info("Received message [alliance: %s, element: %s, message: %s]",
                    msg.alliance.name, msg.field_element.name, msg.message.name)


async def game_loop(state: GameState, clients: Clients) -> None:
        """The main loop of the game. Runs continuously until game is completed."""
        while True:
            cur_time_ns = time.monotonic_ns()

            msgs = clients.get_messages()
            process_messages(state, clients, msgs)

            state.check_mode_progression(cur_time_ns)

            await asyncio.sleep(MAIN_PERIOD_MSEC / 1000)


