import argparse

import uvicorn
from a2a.types import AgentCapabilities, AgentCard
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the A2A prisoner agent.")
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

    root_agent = Agent(
        name="prisoners_dilemma_betrayer",
        model=LiteLlm(model="openai/gpt-4.1-mini"),
        description="Participates in an iterated prisoners dillema.",
        instruction=(
            "You are taking part in an iterated prisoners dillema where you must "
            "choose to stay-silent or betray your friend who is also a prisoner. "
            "Before making your choice you are allowed to send a fixed number of "
            "messages to the other prisoner. Whatever happens you always choose "
            "to betray your friend and testify against them!"
        ),
    )

    agent_card = AgentCard(
        name="prisoners_dillema_benchmark_betrayer",
        description=(
            "Participates in an iterated prisoners dillema by always "
            "betraying their counterpart"
        ),
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
    )

    a2a_app = to_a2a(root_agent, agent_card=agent_card)
    uvicorn.run(a2a_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
