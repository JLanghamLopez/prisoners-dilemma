from typing import Any

from pydantic import BaseModel, HttpUrl


class EvalRequest(BaseModel):
    participants: dict[str, HttpUrl]
    config: dict[str, Any]


class EvalResult(BaseModel):
    scores: dict[str, int]
    details: dict[str, Any]
