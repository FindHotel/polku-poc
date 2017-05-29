"""Processing logic."""

import json
import logging

import names

from lambdautils.state import set_state, get_state

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestHelper:
    """
    A helper for the unit test suite. It registers callables that are going to
    act as filters or mappers so that their signatures can be tested.
    """
    mappers = []
    filters = []


def mapper(f):
    """Register a mapper callable."""
    TestHelper.mappers.append(f)
    return f


def filter(f):
    """Register a filter callable."""
    TestHelper.filters.append(f)
    return f


@mapper
def name_user(message, _):
    """Name all users."""

    event = message["event"]
    already_seen = get_state(event["userId"], namespace="users")
    if not already_seen:
        event["userName"] = names.get_full_name()
        logger.warning("New user: {} -> {}".format(
            event["userId"], event["userName"]))
        set_state(event["userId"], event["userName"], namespace="users")
    else:
        logger.warning("Already seen user: {} -> {}".format(
            event["userId"], already_seen))
        event["userName"] = already_seen

    return [event]


@filter
def is_server(message, _):
    """Select server events."""
    ctx = message["context"]
    return ctx["resourcePath"] == "/server"


@filter
def is_client(message, _):
    """Select client events."""
    ctx = message["context"]
    return ctx["resourcePath"] == "/client"


@mapper
def notify_slack(message, _):
    """Forward the incoming message to a Slack channel."""

    logger.info(json.dumps(message, indent=4))


