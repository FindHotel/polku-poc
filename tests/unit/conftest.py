"""Unit test suite fixtures."""

import pytest


@pytest.fixture(autouse=True)
def mock_state(monkeypatch):
    """Set humilis environment variables."""

    class State:
        def __init__(self):
            self.state = {}

        def get_state(self, key, **kwargs):
            return self.state.get(key)

        def set_state(self, key, value, **kwargs):
            self.state.update({key: value})

    state = State()
    monkeypatch.setattr("polku_poc.processor.set_state", state.set_state)
    monkeypatch.setattr("polku_poc.processor.get_state", state.get_state)
