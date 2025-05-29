import asyncio
import logging
from pathlib import Path
import sys

import click
from nio import AsyncClient  # type: ignore[import-untyped]

from matrix_bot.handlers import DockerHandlers, BaseEventHandlers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@click.command(name='run_matrix_bot')
@click.option('--matrix-server', help='Matrix homeserver URL')
@click.option('--username', help='Matrix bot username')
@click.option('--password', help='Matrix bot password')
@click.option(
    '--rooms', default=None, help='Room IDs. Bot will join this rooms on the start'
)
def cli_handler(matrix_server: str, username: str, password: str, rooms: list[str] | None):
    if rooms is None:
        rooms = []
    asyncio.run(main(matrix_server, username, password, rooms))


async def main(server_url: str, username: str, password: str, rooms: list[str]):
    client = AsyncClient(server_url, username)
    logger.info('Login to Matrix server...')
    await client.login(password)

    [await client.join(room) for room in rooms]

    next_batch_file = Path('matrix_events_batch')

    docker_handlers = DockerHandlers(client, command_prefix='!docker')
    docker_handlers.register_all_handlers()

    base_handler = BaseEventHandlers(client)
    base_handler.register_all_handlers()

    if next_batch_file.exists():
        with open(next_batch_file, "r") as next_batch_token:
            client.next_batch = next_batch_token.read()

    with open(next_batch_file, "w") as next_batch_token:
        while True:
            sync_response = await client.sync(30_000)
            next_batch_token.write(sync_response.next_batch)  # type: ignore


if __name__ == '__main__':
    try:
        cli_handler()
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
