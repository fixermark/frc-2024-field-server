from typing import Final

import asyncio
import logging
import math
import time
from frc_2024_field_server.game import actions
from frc_2024_field_server.game.messages import Score, AmpButtonPressed, CoopertitionButtonPressed
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.game.modes import Mode
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
        elif isinstance(msg.message, CoopertitionButtonPressed):
            alliance = state.alliances[msg.alliance]
            if alliance.coopertition_offered:
                return
            if alliance.banked_notes > 0 and state.coopertition_available():
                await actions.offer_coopertition(state, clients, msg.alliance)




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

async def check_coopertition_update(state: GameState, clients: Clients) -> None:
    """Check to see if we need to update the coopertition status light.

    Coopertition status might go unavailable at the end of the opening 45-sec period.
    """
    if not state.coopertition_available(state.cur_time_ns) and state.coopertition_available(state.prev_time_ns):
        await actions.update_coopertition_lights(state, clients)

async def game_loop(state: GameState, clients: Clients) -> None:
    """The main loop of the game. Runs continuously until game is completed."""
    while True:
        state.prev_time_ns = state.cur_time_ns
        state.cur_time_ns = time.monotonic_ns()

        if state.first_game_frame:
            state.first_game_frame = False
            await actions.update_amp_status_light(state, clients, Alliance.BLUE)
            await actions.update_amp_status_light(state, clients, Alliance.RED)
            await actions.update_coopertition_lights(state, clients)

        new_clients = clients.get_new_clients()
        for client in new_clients:
            await client.send_init_state(state)

        msgs = clients.get_messages()
        await process_messages(state, clients, msgs)

        if state.game_active():
            await update_amp_timer(state, clients, Alliance.BLUE)
            await update_amp_timer(state, clients, Alliance.RED)

            await check_coopertition_update(state, clients)

        prev_mode = state.current_mode
        state.check_mode_progression()

        if prev_mode is Mode.TELEOP and state.current_mode is Mode.SETUP:
            await actions.set_speaker_amp_display(state, clients, Alliance.BLUE, 0)
            await actions.set_speaker_amp_display(state, clients, Alliance.RED, 0)


        await asyncio.sleep(MAIN_PERIOD_MSEC / 1000)



