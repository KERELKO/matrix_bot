from dataclasses import dataclass
from functools import cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(repr=False, slots=True, frozen=True)
class Config:
    matrix_homeserver_url: str | None = os.getenv('MATRIX_HOMESERVER_URL', None)
    matrix_bot_username: str | None = os.getenv('MATRIX_BOT_USERNAME', None)
    matrix_bot_password: str | None = os.getenv('MATRIX_BOT_PASSWORD', None)
    matrix_bot_access_token: str | None = os.getenv('MATRIX_BOT_ACCESS_TOKEN', None)
    matrix_device_id: str | None = os.getenv('MATRIX_DEVICE_ID', None)


@cache
def config_factory() -> Config:
    return Config()
