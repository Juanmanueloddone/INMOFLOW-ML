from pydantic import BaseModel


class VersionInfo(BaseModel):
service: str
version: str
