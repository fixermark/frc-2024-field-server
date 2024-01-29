from typing import Final

import asyncio
import logging
import time
from frc_2024_field_server.game import actions
from frc_2024_field_server.game.messages import Score
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.clients import Clients, ClientMessage
from frc_2024_field_server.message_receiver import Alliance, FieldElement

"""The main game loop."""

logger = logging.getLogger(__name__)

MAIN_PERIOD_MSEC: Final = 50

async def process_messages(state: GameState, clients: Clients, msgs: list[ClientMessage]) -> None:
    """Process incoming messages."""
    for msg in msgs:
        logger.debug("Received message [alliance: %s, element: %s, message: %s]",
                    msg.alliance.name, msg.field_element.name, msg.message)

    if not state.game_active():
        return

    for msg in msgs:
        if isinstance(msg.message, Score):
            if msg.message.element is FieldElement.AMP:
                await actions.score_amp_note(state, clients, msg.alliance)
            else:
                await actions.score_speaker_note(state, clients, msg.alliance)



async def game_loop(state: GameState, clients: Clients) -> None:
        """The main loop of the game. Runs continuously until game is completed."""
        while True:
            state.cur_time_ns = time.monotonic_ns()

            msgs = clients.get_messages()
            await process_messages(state, clients, msgs)

            state.check_mode_progression()

            await asyncio.sleep(MAIN_PERIOD_MSEC / 1000)


