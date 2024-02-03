import math
from frc_2024_field_server.client import Client
from frc_2024_field_server.message_receiver import Alliance, FieldElement, Receiver
from frc_2024_field_server.game.messages import Score, AmpButtonPressed, CoopertitionButtonPressed
from frc_2024_field_server.game.modes import Mode
from frc_2024_field_server.game.state import GameState
"""Clients specific to the game."""

class UnknownClientException(Exception):
    """The specified client does not exist."""

class AmpClient(Client):
    def handle_input(self, inp: str) -> None:
        if inp[0] == "R":
            if inp[1] == "A":
                self.send_message(Score(FieldElement.AMP))
            elif inp[1] == "S":
                self.send_message(Score(FieldElement.SPEAKER))
            else:
                self.report_unknown_input(inp)
                return
        elif inp[0] == "A":
            self.send_message(AmpButtonPressed())
        elif inp[0] == "C":
            self.send_message(CoopertitionButtonPressed())
        else:
            self.report_unknown_input(inp)

    async def send_init_state(self, state: GameState) -> None:
        alliance_state = state.alliances[self.alliance]

        # amp light init
        amp_light_high = "0"

        if alliance_state.amp_end_ns:
            amp_light_high = "B"
        elif alliance_state.banked_notes > 1:
            amp_light_high = "1"

        amp_light_low = "1" if alliance_state.banked_notes > 0 else "0"

        # coopertition status init
        coopertition_light = "0"
        if state.coopertition_accepted() or alliance_state.coopertition_offered:
            coopertition_light = "1"
        elif state.coopertition_available() or state.current_mode in [Mode.AUTONOMOUS, Mode.WAIT_FOR_TELEOP]:
            coopertition_light = "B"

        await self.output(f'L{amp_light_low}')
        await self.output(f'H{amp_light_high}')
        await self.output(f'C{coopertition_light}')

class SpeakerClient(Client):
    def handle_input(self, inp: bytes) -> None:
        if inp[0] == "R":
            if inp[1] == "A":
                self.send_message(Score(FieldElement.AMP))
            elif inp[1] == "S":
                self.send_message(Score(FieldElement.SPEAKER))
            else:
                self.report_unknown_input(inp)
                return
        else:
            self.report_unknown_input(inp)

    async def send_init_state(self, state: GameState) -> None:
        remaining_amp_time_ns = state.alliances[self.alliance].get_remaining_amp_time_ns(state.cur_time_ns)
        remaining_amp_time_secs = math.ceil(remaining_amp_time_ns / 1e9)

        msg = "A" if remaining_amp_time_secs >= 10 else str(remaining_amp_time_secs)
        await self.output(f'A{msg}')




def new_client(alliance: Alliance, element: FieldElement, receiver: Receiver) -> Client:
    if element == FieldElement.AMP:
        return AmpClient(alliance, element ,receiver)
    elif element == FieldElement.SPEAKER:
        return SpeakerClient(alliance, element, receiver)
    else:
        raise UnknownClientException(f"No client for {element.name}")
