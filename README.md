# Prisoners

***The Iterated Prisoners Dilemma for LLM Agents***

Prisoners implements the
[iterated prisoners dillema](https://en.wikipedia.org/wiki/Prisoner%27s_dilemma#The_iterated_prisoner's_dilemma)
with the added twist that the agents can communicate prior to selecting their choice.

Each round of the game each agent:

- Participates in a brief conversation with their counterpart
- Then responds with `testify` to testify against their counterpart, or `silence` to remain silent.

As per the prisoner's dilemma, each agent is sentenced to:

- 1 year each if both agents stay silent
- 2 years if they both testify
- 3 years if they stay silent and their counterpart testifies
- 0 years if they testify and their counterpart stays silent

if an agent makes a choice that is not recognised (i.e. it is not one of
`testify` or `silent`) this is treated as the agent being silent.

The final score assigned to each agent is the sum of their sentences across several rounds.

## Developers

Dependencies can be installed with [poetry](https://python-poetry.org/) by running

```commandline
poetry install
```

which will create a virtual environment in the repo at `.venv` which can
be activated with

```commandline
source .venv/bin/activate
```

The scenario can be run locally with

```commandline
python -m prisoners.run_scenario scenario.toml
```

the parameters of the scenario can be specified in `scenario.toml` and
an API key provided in an `.env` file (see `sample.env` for an example).
