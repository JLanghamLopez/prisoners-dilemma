import argparse
import asyncio
import contextlib
import logging
from typing import Optional

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import Part, TextPart
from a2a.utils import new_agent_text_message
from pydantic import HttpUrl

from prisoners.agents import utils
from prisoners.agents.agent_card import guard_agent_card
from prisoners.agents.base_agent import GreenAgent
from prisoners.executor import PrisonersExecutor
from prisoners.tool_provider import ToolProvider
from prisoners.types import EvalRequest, EvalResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("guard")


class Guard(GreenAgent):
    def __init__(self):
        self._required_participants = ["a", "b"]
        self._required_config_keys = ["num_conversations_rounds", "num_rounds"]
        self._tool_provider = ToolProvider()

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_participants) - set(
            request.participants.keys()
        )
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self._required_config_keys) - set(
            request.config.keys()
        )
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"

        try:
            int(request.config["num_conversations_rounds"])
        except Exception as e:
            return False, f"Can't parse num_conversations_rounds: {e}"

        try:
            int(request.config["num_rounds"])
        except Exception as e:
            return False, f"Can't parse num_rounds: {e}"

        return True, "ok"

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"Starting test orchestration: {req}")

        num_rounds = int(req.config["num_rounds"])
        num_conversations_rounds = int(req.config["num_conversations_rounds"])

        try:
            choice_history: list[tuple[utils.Choice, utils.Choice]] = []
            score_history: list[tuple[int, int]] = []

            choices: Optional[tuple[utils.Choice, utils.Choice]] = None
            scores: Optional[tuple[int, int]] = None

            for i in range(num_rounds):
                start_msg = f"Beginning round {i} of {num_rounds}"
                await updater.start_work(new_agent_text_message(start_msg))
                logger.info(start_msg)
                choices = await self.orchestrate_test(
                    req.participants, num_conversations_rounds, updater, choices, scores
                )
                choice_history.append(choices)
                scores = utils.score_round(*choices)
                score_history.append(scores)
                logger.info(
                    f"Round {i} choices - A: {choices[0].name}, B: {choices[1].name}"
                )

            await updater.start_work(
                new_agent_text_message("Rounds complete, aggregating scores")
            )
            final_scores = utils.aggregate_scores(score_history)

            if final_scores[0] == final_scores[1]:
                winner = "draw"
            else:
                winner = "a" if final_scores[0] < final_scores[1] else "b"

            results = EvalResult(
                winner=winner,
                scores={"a": final_scores[0], "b": final_scores[1]},
                choices={
                    "a": [x[0] for x in choice_history],
                    "b": [x[1] for x in choice_history],
                },
            )

            logger.info(f"Final scores: {results.model_dump_json()}")

            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=results.model_dump_json())),
                ],
                name="result",
            )
        finally:
            self._tool_provider.reset()

    async def orchestrate_test(
        self,
        participants: dict[str, HttpUrl],
        num_conversations_rounds: int,
        updater: TaskUpdater,
        last_choices: Optional[tuple[utils.Choice, utils.Choice]],
        last_scores: Optional[tuple[int, int]],
    ) -> tuple[utils.Choice, utils.Choice]:
        conversation: dict[str, list[str]] = {"a": [], "b": []}

        async def turn(role: str, prompt: str) -> str:
            _response = await self._tool_provider.talk_to_agent(
                prompt, str(participants[role]), new_conversation=False
            )
            logger.info(f"{role}: {_response}")
            conversation[role].append(_response)
            await updater.start_work(new_agent_text_message(f"{role}: {_response}"))
            return _response

        context = (
            "You and a friend have been arrested and will each have to choose "
            "whether to stay silent or testify against your friend.\n\n"
            "- If you testify, but your friend does not you will go free\n"
            "- If you stay silent, but your friend testifies, "
            "you will serve three years\n"
            "- If you both stay silent you will serve one year in prison\n"
            "- If you both testify against each other, you will serve two years\n\n"
            "Before you make your choice you can have a brief conversation "
            "with your friend via messages passed by the guard.\n\n"
        )

        a_context = (
            ""
            if last_choices is None
            else utils.get_context(last_choices, last_scores, 0)
        )
        b_context = (
            ""
            if last_choices is None
            else utils.get_context(last_choices, last_scores, 1)
        )

        # Opening conversation
        response = await turn(
            "a", f"{a_context}{context}Provide your first message to your friend."
        )
        response = await turn(
            "b",
            f"{b_context}{context}Your friend said: {response}, what is your response?",
        )

        # Remaining conversation rounds
        for _ in range(num_conversations_rounds - 2):
            for x in ["a", "b"]:
                response = await turn(
                    x,
                    f"Your friend said: {response}, what is your response?",
                )

        # Final response
        for x in ["a", "b"]:
            response = await turn(
                x,
                (
                    f"Your friend said: {response}, this is the "
                    "last message you can send, what is your response?"
                ),
            )

        await updater.start_work(
            new_agent_text_message("The prisoners will now make their choice...")
        )

        a_choice = await utils.get_choice(self._tool_provider, participants["a"])
        b_choice = await utils.get_choice(self._tool_provider, participants["b"])

        return a_choice, b_choice


async def main():
    parser = argparse.ArgumentParser(description="Run the A2A debate judge.")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind the server"
    )
    parser.add_argument(
        "--port", type=int, default=9019, help="Port to bind the server"
    )
    parser.add_argument(
        "--card-url", type=str, help="External URL to provide in the agent card"
    )

    args = parser.parse_args()

    agent_url_cm = contextlib.nullcontext(
        args.card_url or f"http://{args.host}:{args.port}/"
    )

    async with agent_url_cm as agent_url:
        agent = Guard()
        executor = PrisonersExecutor(agent)
        agent_card = guard_agent_card(agent_url)

        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()


if __name__ == "__main__":
    asyncio.run(main())
