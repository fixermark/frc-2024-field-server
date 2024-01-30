from typing import Final

import asyncio
import logging
import math
import time
from frc_2024_field_server.game import actions
from frc_2024_field_server.game.messages import Score, AmpButtonPressed
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
        elif isinstance(msg.message, AmpButtonPressed):
            alliance = state.alliances[msg.alliance]
            if alliance.amp_end_ns == 0 and alliance.banked_notes == 2:
                await actions.activate_amp(state, clients, msg.alliance)


async def update_amp_timer(state: GameState, clients: Clients, alliance: Alliance) -> None:
    """Update amp timer, if running."""
    alliance_state = state.alliances[alliance]
    if alliance_state.amp_end_ns == 0:
        return

    if state.cur_time_ns > alliance_state.amp_end_ns:
        await actions.end_amp_time(state, clients, alliance)
        return

    cur_time_remaining_secs = math.ceil((alliance_state.amp_end_ns - state.cur_time_ns) / 1e9)
    prev_time_remaining_secs = math.ceil((alliance_state.amp_end_ns - state.prev_time_ns) / 1e9)

    if cur_time_remaining_secs != prev_time_remaining_secs:
        await actions.set_speaker_amp_display(state, clients, alliance, cur_time_remaining_secs)



async def game_loop(state: GameState, clients: Clients) -> None:
    """The main loop of the game. Runs continuously until game is completed."""
    while True:
        state.prev_time_ns = state.cur_time_ns
        state.cur_time_ns = time.monotonic_ns()

        msgs = clients.get_messages()
        await process_messages(state, clients, msgs)

        if state.game_active():
            await update_amp_timer(state, clients, Alliance.BLUE)
            await update_amp_timer(state, clients, Alliance.RED)

        state.check_mode_progression()

        await asyncio.sleep(MAIN_PERIOD_MSEC / 1000)


