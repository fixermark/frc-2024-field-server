"""Discrete mutations to game state.

Actions may modify state and update field elements in relation to new state.
"""

from frc_2024_field_server.game.constants import AMP_NOTE_SCORE_FOR_MODE, AMPLIFIED_SPEAKER_NOTE_SCORE, UNAMPLIFIED_SPEAKER_NOTE_SCORE_FOR_MODE, AMP_TIME_NS
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.clients import Clients
from frc_2024_field_server.message_receiver import Alliance, FieldElement

async def score_amp_note(state: GameState, clients: Clients, alliance: Alliance):
    """Score a note to the amp and update amp field displays."""
    points = AMP_NOTE_SCORE_FOR_MODE[state.current_mode]

    alliance_state = state.alliances[alliance]

    alliance_state.score += points

    if alliance_state.banked_notes < 2:
        alliance_state.banked_notes += 1

    await update_amp_status_light(state, clients, alliance)

async def update_amp_status_light(state: GameState, clients: Clients, alliance: Alliance):
    """Update the status light on the amp to reflect banked notes and amp mode."""
    alliance_state = state.alliances[alliance]

    low_light_message = "L1" if alliance_state.banked_notes >=1 else "L0"
    if alliance_state.banked_notes >= 1:
        await clients.output(alliance, FieldElement.AMP, low_light_message)

    if alliance_state.amp_end_ns != 0:
        await clients.output(alliance, FieldElement.AMP, "HB")
    else:
        high_light_message = "H1" if alliance_state.banked_notes >= 2 else "H0"
        await clients.output(alliance, FieldElement.AMP, high_light_message)

async def score_speaker_note(state: GameState, clients: Clients, alliance: Alliance):
    """Score a note in the speaker."""
    alliance_state = state.alliances[alliance]
    if alliance_state.amp_end_ns != 0:
        alliance_state.score += AMPLIFIED_SPEAKER_NOTE_SCORE
    else:
        alliance_state.score += UNAMPLIFIED_SPEAKER_NOTE_SCORE_FOR_MODE[state.current_mode]

async def activate_amp(state: GameState, clients: Clients, alliance: Alliance):
    alliance_state = state.alliances[alliance]
    alliance_state.banked_notes -= 2
    alliance_state.amp_end_ns = state.cur_time_ns + AMP_TIME_NS
    await update_amp_status_light(state, clients, alliance)

async def end_amp_time(state: GameState, clients: Clients, alliance: Alliance):
    alliance_state = state.alliances[alliance]
    alliance_state.amp_end_ns = 0
    await update_amp_status_light(state, clients, alliance)
