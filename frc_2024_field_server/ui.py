"""Tkinter UI for the field server"""

import asyncio
from tkinter import Tk, RIDGE
from tkinter import ttk
from tkinter.font import Font
from frc_2024_field_server.clients import Clients
from frc_2024_field_server.client import Client
from frc_2024_field_server.message_receiver import Alliance, FieldElement
from frc_2024_field_server.game.modes import Mode
from frc_2024_field_server.game.state import GameState
from typing import Final

MODE_TO_NAME: Final = {
    Mode.SETUP: 'Setup',
    Mode.AUTONOMOUS: 'Autonomous',
    Mode.WAIT_FOR_TELEOP: '(wait for Teleop)',
    Mode.TELEOP: 'Teleop',
}

class UI:
    def __init__(self, clients: Clients, state: GameState):
        self._clients = clients
        self._state = state

        self._root = Tk()
        self._root.title("Crescendo Field Server")
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(0, weight=1)
        # TODO: root should not be closeable
        self._root.bind("<space>", self.handle_keypress)

        # Setup fonts
        self._category_font = Font(size=24)
        self._score_font = Font(size=48)

        # setup styles
        self._styles = [
            ttk.Style().configure("connection_off.TLabel", background="#ff9999"),
            ttk.Style().configure("connection_on.TLabel", background="#99ff99"),
        ]

        self._topframe = ttk.Frame(self._root, padding=10)
        self._topframe.grid(row = 0, column = 0, sticky="nwse")
        self._topframe.grid_columnconfigure(0, weight=1)

        self._connections = ttk.Frame(self._topframe, padding=5)
        self._connections.grid(row=0, column = 0, sticky="nwe")
        self._connections.grid_columnconfigure(0, weight=1)
        self._connections.grid_columnconfigure(1, weight=1)
        self._connections.grid_rowconfigure(0, weight=1)
        self._connections.grid_rowconfigure(1, weight=1)

        self._red_speaker_connection = self._init_connection(self._connections, 0, 0, "Red Speaker")
        self._blue_speaker_connection = self._init_connection(self._connections, 0, 1, "Blue Speaker")
        self._red_amp_connection = self._init_connection(self._connections, 1, 0, "Red Amp")
        self._blue_amp_connection = self._init_connection(self._connections, 1, 1, "Blue Amp")

        self._scores = ttk.Frame(self._topframe, padding=5)
        self._scores.grid(row=1, column=0, sticky="we")
        self._scores.grid_columnconfigure(0, weight=1)
        self._scores.grid_columnconfigure(1, weight=1)

        self._red_score_label = self._init_score(self._scores, 0, "Red Alliance")
        self._blue_score_label = self._init_score(self._scores, 1, "Blue Alliance")

        time_frame = ttk.Frame(self._topframe, padding=5)
        time_frame.grid(row=2, column=0, sticky="wes")
        time_frame.grid_columnconfigure(0, weight=1)

        self._time_mode_label = ttk.Label(time_frame, padding=5, text="Setup", font=self._category_font, justify="center")
        self._time_mode_label.grid(row=0, column=0)

        self._time_count_label = ttk.Label(time_frame, padding=5, text="0.0", font=self._score_font, justify="center")
        self._time_count_label.grid(row=1, column=0)


    def handle_keypress(self, _)-> None:
        """Handle a keypress event in the UI."""
        self._state.handle_go_button()


    def _init_connection(self, parent: ttk.Frame, row: int, column: int, label: str) -> ttk.Label:
        """Add a connection status panel in the specified location and return it."""
        label_widget = ttk.Label(parent, text=label, padding=10, relief=RIDGE, borderwidth=5)
        label_widget.grid(row=row, column=column, sticky="nwse")
        return label_widget

    def _init_score(self, parent: ttk.Frame, column: int, label: str) -> ttk.Label:
        """Adds a score panel in the specified column with the specified label.

        Args:
          parent: Which frame to put the score in.
          column: Which column to put the score in.
          label: Label of score.

        Return:
          The value label that can be updated to show score.
        """
        score_frame = ttk.Frame(parent, padding=5)
        score_frame.grid(row=0, column=column)
        score_frame.grid_columnconfigure(0, weight=1)

        top_label = ttk.Label(score_frame, text=label, font=self._category_font, justify="center")
        top_label.grid(row=0, column=0)

        value_label = ttk.Label(score_frame, text="0", font=self._score_font, justify="center")
        value_label.grid(row=1, column=0)
        return value_label

    async def update(self):
        """Run an update on the UI to allow for repaints and events."""
        while True:
            self._update_connection_states(self._clients)
            self._update_scores(self._state)
            self._update_mode_and_time(self._state)

            self._root.update()
            await asyncio.sleep(0)


    def _update_connection_states(self, clients: Clients) -> None:
        """Update connection display."""
        self._update_connection_state(self._red_speaker_connection, clients.clients[Alliance.RED][FieldElement.SPEAKER])
        self._update_connection_state(self._blue_speaker_connection, clients.clients[Alliance.BLUE][FieldElement.SPEAKER])
        self._update_connection_state(self._red_amp_connection, clients.clients[Alliance.RED][FieldElement.AMP])
        self._update_connection_state(self._blue_amp_connection, clients.clients[Alliance.BLUE][FieldElement.AMP])

    def _update_connection_state(self, label: ttk.Label, client: Client | None):
        """Set the color of a connection label based on connection status."""
        label.config(style="connection_off.TLabel" if client is None else "connection_on.TLabel")

    def _update_scores(self, state: GameState) -> None:
        """Update the score displays."""
        self._red_score_label.config(text=state.alliances[Alliance.RED].score)
        self._blue_score_label.config(text=state.alliances[Alliance.BLUE].score)

    def _update_mode_and_time(self, state: GameState) -> None:
        """Update the current time remaining and the current game mode."""
        self._time_mode_label.config(text=MODE_TO_NAME[state.current_mode])

        remaining_time_ns = state.get_remaining_time_ns()
        remaining_time_secs = round(remaining_time_ns / 1e9 ,1)
        self._time_count_label.config(text=remaining_time_secs)

