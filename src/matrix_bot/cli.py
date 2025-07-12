import asyncio
import logging
from pathlib import Path
import sys
from typing import Iterable

import click
from nio import AsyncClient  # type: ignore[import-untyped]

from matrix_bot.handlers import DockerHandlers, BaseEventHandlers
from matrix_bot.config import config_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@click.command(name='run_matrix_bot')
@click.option('--matrix-server', help='Matrix homeserver URL', default=None)
@click.option('--username', help='Matrix bot username', default=None)
@click.option('--password', help='Matrix bot password', default=None)
@click.option(
    '--rooms', default=None, help='Room IDs. Bot will join this rooms on the start'
)
def cli_handler(
    rooms: list[str] | None,
    matrix_server: str | None = None,
    username: str | None = None,
    password: str | None = None,
):
    if rooms is None:
        rooms = []
    asyncio.run(main(matrix_server, username, password, rooms))


async def main(
    matrix_server: str | None,
    username: str | None,
    password: str | None,
    rooms: Iterable[str] = (),
):
    config = config_factory()
    matrix_server = matrix_server or config.matrix_homeserver_url
    username = username or config.matrix_bot_username
    password = password or config.matrix_bot_password

    # TODO: remove
    print(
        f'{matrix_server=}, {username=}, {password=},'
        f'{config.matrix_bot_access_token=}, {config.matrix_device_id}'
    )

    if matrix_server is None or username is None:
        raise ValueError(
            'Invalid input paramters or some parameters are missing:\n'
            f'username={username}, matrix_server={matrix_server}'
        )
    if not password and not config.matrix_bot_access_token:
        raise ValueError(f'Password or access token was not provided for matrix user "{username}"')

    client = AsyncClient(matrix_server, username)

    if password:
        logger.info('Login to Matrix server with password...')
        await client.login(password=password)

    if config.matrix_bot_access_token:
        client.access_token = config.matrix_bot_access_token
        client.device_id = config.matrix_device_id

    [await client.join(room) for room in rooms]

    next_batch_file = Path('matrix_events_batch')

    docker_handlers = DockerHandlers(client, command_prefix='!docker')
    docker_handlers.register_all_handlers()

    base_handler = BaseEventHandlers(client)
    base_handler.register_all_handlers()

    if next_batch_file.exists():
        with open(next_batch_file, "r") as next_batch_token:
            client.next_batch = next_batch_token.read()

    while True:
        sync_response = await client.sync(30_000)
        with open(next_batch_file, "w") as next_batch_token:
            next_batch_token.write(sync_response.next_batch)  # type: ignore


if __name__ == '__main__':
    try:
        cli_handler()
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
