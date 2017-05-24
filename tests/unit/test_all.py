"""Test the processing logic."""

import pytest

from polku_poc.processor import TestHelper, name_user, is_server


def test_dummy():
    """Dummy test."""
    pass


@pytest.mark.parametrize("message", [
    {},
    {"key": "value"}])
def test_mapper_signature(message):
    """Test that mappers comply with mapper signature."""
    for mapper in TestHelper.mappers:
        context = {}
        try:
            output = mapper(message, context)
        except TypeError:
            # Not complying with the mapper signature
            raise
        except Exception:
            output = []

        assert isinstance(output, list) \
            and all(isinstance(x, dict) for x in output)


@pytest.mark.parametrize("message", [
    {},
    {"key": "value"}])
def test_filter_signature(message):
    """Test that filters comply with filter signature."""
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
    ev = name_user(message, {})[0]
    assert "userName" in ev
    original_name = ev["userName"]
    assert name_user(message, {})[0]["userName"] == original_name


@pytest.mark.parametrize("message, outcome", [
    [{"event": {"userId": "x", "context": {"resourcePath": "/server"}}}, True],
    [{"event": {"userId": "x", "context": {"resourcePath": "/client"}}}, False],
    ])
def test_is_server(message, outcome):
    """Test name_user mapper."""
    assert is_server(message, {}) == outcome
