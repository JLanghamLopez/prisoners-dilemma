from enum import Enum
from typing import Any

from pydantic import BaseModel, HttpUrl


class Choice(Enum):
    testify = 0
    silence = 1
    unrecognised = 2


class EvalRequest(BaseModel):
    participants: dict[str, HttpUrl]
    config: dict[str, Any]


class EvalResult(BaseModel):
    winner: str
    scores: dict[str, int]
    choices: dict[str, list[str]]
