from pydantic import BaseSettings


class Settings(BaseSettings):
    PATH_TOKEN: str = '/tmp/token.json'
    PATH_TO_SECRETS: str = '/tmp/secrets.json'
    SHEET_ID: str
