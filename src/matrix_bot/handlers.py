import subprocess
from logging import getLogger

from nio import (AsyncClient, JoinError,  # type: ignore[import-untyped]
                 MatrixRoom, RoomMessageText)
from nio.events import InviteEvent  # type: ignore[import-untyped]

logger = getLogger()


class DockerHandlers:
    def __init__(
        self,
        nio_client: AsyncClient,
        command_prefix: str,
    ):
        self.nio_client = nio_client
        self.command_prefix = command_prefix

    async def execute_raw_command(self, room: MatrixRoom, event: RoomMessageText):
        if not event.body.startswith(self.command_prefix):
            return

        logger.info('Processing raw docker command')
        docker_command_splitted = event.body.split(' ')[1:]
        docker_command = ' '.join(docker_command_splitted)

        result = subprocess.run(docker_command, shell=True, check=True, capture_output=True)
        if result.stderr:
            logger.info('Error occured while executing docker command')
            await self.nio_client.room_send(
                room_id=room.room_id,
                message_type='m.room.message',
                content={'msgtype': 'm.text', 'body': result.stderr.decode()}
            )
            return
        elif result.stdout:
            logger.info('Docker command executed without errors')
            await self.nio_client.room_send(
                room_id=room.room_id,
                message_type='m.room.message',
                content={'msgtype': 'm.text', 'body': result.stdout.decode()}
            )
            return
        else:
            logger.info("Failed to identify user message")
            await self.nio_client.room_send(
                room_id=room.room_id,
                message_type='m.room.message',
                content={'msgtype': 'm.text', 'body': 'Failed to identify your input'}
            )
            return

    def register_all_handlers(self):
        self.nio_client.add_event_callback(self.execute_raw_command, filter=RoomMessageText)  # type: ignore # noqa


class BaseEventHandlers:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def join_room_event_handler(self, room: MatrixRoom, event: InviteEvent):
        logger.info('Processing "join_room_event_handler" handler')
        response = await self.client.join(room.room_id)
        if isinstance(response, JoinError):
            logger.error(f'Failed to join room: {response}')
            return
        logger.info(f'Successfully joined room: room_id={room.room_id}')

    def register_all_handlers(self):
        self.client.add_event_callback(self.join_room_event_handler, InviteEvent)  # type: ignore
