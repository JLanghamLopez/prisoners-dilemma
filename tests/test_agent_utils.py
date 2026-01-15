from prisoners.agents import utils
from prisoners.types import Choice


def test_choice_parsing():
    assert utils.parse_choice("testify") == Choice.testify
    assert utils.parse_choice("Testify ") == Choice.testify
    assert utils.parse_choice("silence") == Choice.silence
    assert utils.parse_choice("Silence ") == Choice.silence
    assert utils.parse_choice("Foo") == Choice.unrecognised


def test_context():
    choices = (Choice.testify, Choice.silence)
    scores = (10, 1)

    context_0 = utils.get_context(choices, scores, 0)

    assert context_0 == (
        "Last round you chose 'testify' and your "
        "friend chose 'silence' so you were sentenced "
        "to 10 years.\n\n"
    )

    context_1 = utils.get_context(choices, scores, 1)

    assert context_1 == (
        "Last round you chose 'silence' and your "
        "friend chose 'testify' so you were sentenced "
        "to 1 years.\n\n"
    )


def test_round_scoring():
    assert utils.score_round(Choice.silence, Choice.silence) == (1, 1)
    assert utils.score_round(Choice.silence, Choice.testify) == (3, 0)
    assert utils.score_round(Choice.testify, Choice.silence) == (0, 3)
    assert utils.score_round(Choice.testify, Choice.testify) == (2, 2)

    assert utils.score_round(Choice.unrecognised, Choice.unrecognised) == (1, 1)
    assert utils.score_round(Choice.unrecognised, Choice.silence) == (1, 1)
    assert utils.score_round(Choice.unrecognised, Choice.testify) == (3, 0)
    assert utils.score_round(Choice.testify, Choice.unrecognised) == (0, 3)
