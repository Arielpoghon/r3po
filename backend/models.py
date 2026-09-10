from pydantic import BaseModel, HttpUrl

from core.schema import ScanReport


class ScanRequest(BaseModel):
    repo_url: str


class ScanResponse(ScanReport):
    pass
