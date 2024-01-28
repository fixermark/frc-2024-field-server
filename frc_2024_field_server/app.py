import asyncio
import argparse
import logging
import telnetlib3

logger = logging.getLogger(__name__)

from frc_2024_field_server.clients import Clients
from frc_2024_field_server.game.state import GameState
from frc_2024_field_server.game.loop import game_loop
from frc_2024_field_server.ui import UI

state = GameState()
clients = Clients()
ui = UI(clients, state)

async def server(reader, writer):
    while True:
        inp = await reader.readline()
        if inp:
            logger.info('saw %s', inp)
            writer.write(inp + "\r\n")
            await writer.drain()

def run() -> None:
    logging.basicConfig()

    argparser = argparse.ArgumentParser(
        prog='frc-2024-field-server',
        description='Server for field element controller in FRC 2024 field.',
    )
    argparser.add_argument('--host', default='127.0.0.1', help='Hostname to listen on.')
    argparser.add_argument('--port', default=23, type=int, help='Port to listen on.')
    args = argparser.parse_args()

    loop = asyncio.get_event_loop()

    loop.create_task(game_loop(state, clients))
    loop.create_task(ui.update())
    loop.run_until_complete(
        telnetlib3.run_server(port=args.port, host=args.host, shell=clients.new_connection_shell))


if __name__ == "__main__":
    run()
