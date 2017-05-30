"""Test the processing logic."""

import pytest

from polku_poc.processor import TestHelper, name_user, is_server


TS1 = "2017-05-30T10:33:33.890457+00:00"
TS2 = "2017-05-30 10:33:33"
BASE = {"sentAt": TS1, "receivedAt": TS2}
EVBASE = {"timestamp": TS1}


@pytest.mark.parametrize("message", [
    {"event": {}},
    {"event": {"key": "value"}}])
def test_mapper_signature(message):
    """Test that mappers comply with mapper signature."""
    message.update(BASE)
    message["event"].update(EVBASE)
    for mapper in TestHelper.mappers:
        context = {}
        try:
            output = mapper(message, context)
        except TypeError:
            # Not complying with the mapper signature
            raise
        except Exception:
            output = []

        assert output is None or (isinstance(output, list)
            and all(isinstance(x, dict) for x in output))


@pytest.mark.parametrize("message", [
    {"event": {}},
    {"event": {"key": "value"}}])
def test_filter_signature(message):
    """Test that filters comply with filter signature."""
    message.update(BASE)
    message["event"].update(EVBASE)
    for f in TestHelper.filters:
        context = {}
        try:
            output = f(message, context)
            assert output in (False, True)
        except TypeError:
            # Not complying with the mapper signature
            raise
        except Exception:
            pass


@pytest.mark.parametrize("message", [
    {"event": {"userId": "x"}},
    ])
def test_name_user(message):
    """Test name_user mapper."""
    message.update(BASE)
    message["event"].update(EVBASE)
    ev = name_user(message, {})[0]
    assert "user_name" in ev
    original_name = ev["user_name"]
    assert name_user(message, {})[0]["user_name"] == original_name


@pytest.mark.parametrize("message, outcome", [
    [{"event": {"userId": "x"}, "context": {"resourcePath": "/server"}}, True],
    [{"event": {"userId": "x"}, "context": {"resourcePath": "/client"}}, False],
    ])
def test_is_server(message, outcome):
    """Test name_user mapper."""
    message.update(BASE)
    message["event"].update(EVBASE)
    assert is_server(message, {}) == outcome
