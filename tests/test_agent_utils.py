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
        f"Last round you chose 'testify' and your "
        f"friend chose 'silence' so you were sentenced "
        f"to 10 years.\n\n"
    )

    context_1 = utils.get_context(choices, scores, 1)

    assert context_1 == (
        f"Last round you chose 'silence' and your "
        f"friend chose 'testify' so you were sentenced "
        f"to 1 years.\n\n"
    )
