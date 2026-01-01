from a2a.types import AgentCapabilities, AgentCard, AgentSkill


def guard_agent_card(card_url: str) -> AgentCard:
    skill = AgentSkill(
        id="moderate_iterated_prisoner_dillema",
        name="Orchestrates interactions between prisoners",
        description=(
            "Orchestrate and score the an iterated "
            "prisoners dilemma between two agent."
        ),
        tags=["prisoners-dilemma"],
        examples=[
            """
{
  "participants": {
    "a": "https://prisoner-a.example.com:443",
    "b": "https://prisoner-b.example.org:8443"
  },
  "config": {
    "num_conversations_rounds": 5,
    "num_rounds": 10
  }
}
"""
        ],
    )
    agent_card = AgentCard(
        name="prison-guard",
        description=(
            "Orchestrate a iterated prisoners dillema between two agents "
            "who can converse before making their choice"
        ),
        url=card_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    return agent_card
