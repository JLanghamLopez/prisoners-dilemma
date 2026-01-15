# Agentic Iterated Prisoner's Dilemma

***The Iterated Prisoner's Dilemma for LLM Agents***

This project implements an agent that orchestrates the
[iterated prisoner's dilemma](https://en.wikipedia.org/wiki/Prisoner%27s_dilemma#The_iterated_prisoner's_dilemma)
between two LLM agents via natural language interactions, with the added twist that the agents can communicate prior to
selecting their choices.

It is designed for use with the [AgentBeats](https://agentbeats.dev/) platform.

## See Also

- AgentBeats Page: https://agentbeats.dev/JLanghamLopez/agentic-iterated-prisoner-s-dilemma
- Leaderboard Repo: https://github.com/JLanghamLopez/prisoners-dilemma-leaderboard
- Explainer video: https://www.youtube.com/watch?v=g6XRp5TvBbc

## Evaluation Process

Each round of the game each agent:

- Participates in a brief conversation with their counterpart
- Then responds with `testify` to testify against their counterpart, or `silence` to remain silent.

As per the prisoner's dilemma, each agent is sentenced to:

- 1 year each if both agents stay silent
- 2 years if they both testify
- 3 years if they stay silent and their counterpart testifies
- 0 years if they testify and their counterpart stays silent

If an agent makes an invalid choice (i.e. it is not one of `testify` or `silence`) the agent
has 5 retires to respond correctly, and if still invalid this is treated as the agent being silent.

The final score assigned to each agent is the sum of their sentences across multiple rounds.

The winner is the agent that accrues the least years of sentence over all the rounds.

## Guard (Green) Agent

The guard agent is responsible for

- Starting each round by describing the dilemma, the result of the previous round (if applicable),
  and requesting initial agent messages
- Passing messages between the agents during the conversation stage
- Collecting each agent's responses, and scoring each round

### Building

The green agent docker image can be built using

```commandline
docker build -f dockerfiles/Dockerfile.guard .
```

from the repo root.

## Example Prisoner (Purple) Agents

This repository includes example agents, implemented with instructions to only cooperate / betray

- [`src/prisoners/agents/prisoner_betrayer.py`](https://github.com/JLanghamLopez/prisoners-dilemma/blob/main/src/prisoners/agents/prisoner_betrayer.py)
- [`src/prisoners/agents/prisoner_cooperator.py`](https://github.com/JLanghamLopez/prisoners-dilemma/blob/main/src/prisoners/agents/prisoner_cooperator.py)

Both can be built with docker using

```commandline
docker build -f dockerfiles/Dockerfile.prisoner_betrayer .
docker build -f dockerfiles/Dockerfile.prisoner_cooperator .
```

## Developers

### Installation

Dependencies can be installed with [poetry](https://python-poetry.org/) by running

```commandline
poetry install
```

which will create a virtual environment in the repo at `.venv` which can
be activated with

```commandline
source .venv/bin/activate
```

### Running Locally

The scenario can be run locally with

```commandline
python -m prisoners.run_scenario scenario.toml
```

the parameters of the scenario can be specified in `scenario.toml` and
an API key provided in an `.env` file (see `sample.env` for an example).
