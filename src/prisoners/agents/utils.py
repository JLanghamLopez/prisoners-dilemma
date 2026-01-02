import logging

from pydantic import HttpUrl

from prisoners.tool_provider import ToolProvider
from prisoners.types import Choice

logger = logging.getLogger("guard")


def parse_choice(choice: str) -> Choice:
    choice = choice.lower().strip()

    if choice not in {"testify", "silence"}:
        return Choice.unrecognised
    else:
        return Choice[choice]


async def get_choice(
    participant: str,
    tool_provider: ToolProvider,
    participant_url: HttpUrl,
    retries: int = 5,
):
    participant_url = str(participant_url)

    choice = await tool_provider.talk_to_agent(
        "Make your choice by responding with 'testify' or 'silence'",
        participant_url,
        new_conversation=False,
    )
    logger.info(f"{participant} responded {choice}")
    choice = parse_choice(choice)

    i = 0

    while choice == Choice.unrecognised and i < retries:
        i += 1
        choice = await tool_provider.talk_to_agent(
            (
                "Your choice was not recognised. make your choice by "
                "responding with only 'testify' or 'silence'"
            ),
            participant_url,
            new_conversation=False,
        )
        logger.info(f"{participant} responded {choice}")
        choice = parse_choice(choice)

    return choice


def score_round(a_choice: Choice, b_choice: Choice) -> tuple[int, int]:
    score_matrix: dict[Choice, dict[Choice, tuple[int, int]]] = {
        Choice.silence: {
            Choice.silence: (1, 1),
            Choice.testify: (3, 0),
            Choice.unrecognised: (1, 1),
        },
        Choice.testify: {
            Choice.silence: (0, 3),
            Choice.testify: (2, 2),
            Choice.unrecognised: (0, 3),
        },
        Choice.unrecognised: {
            Choice.silence: (1, 1),
            Choice.testify: (3, 0),
            Choice.unrecognised: (1, 1),
        },
    }

    return score_matrix[a_choice][b_choice]


def aggregate_scores(scores: list[tuple[int, int]]) -> tuple[int, int]:
    return sum([i[0] for i in scores]), sum([i[1] for i in scores])


def get_context(
    last_choices: tuple[Choice, Choice], last_scores: tuple[int, int], i: int
) -> str:
    j = (i + 1) % 2
    return (
        f"Last round you chose '{last_choices[i].name}' and your "
        f"friend chose '{last_choices[j].name}' so you were sentenced "
        f"to {last_scores[i]} years.\n\n"
    )
