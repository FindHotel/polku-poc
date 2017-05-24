"""Processing logic."""

import logging
import names

from lambdautils.state import set_state, get_state

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestHelper:
    mappers = []
    filters = []


def mapper(f):
    TestHelper.mappers.append(f)
    return f


def filter(f):
    TestHelper.filters.append(f)
    return f


@mapper
def name_user(message, _):
    """Names all users."""

    event = message["event"]
    already_seen = get_state(event["userId"], namespace="users")
    if not already_seen:
        event["userName"] = names.get_full_name()
        logger.info("{} -> {}".format(event["userId"], event["userName"]))
        set_state(event["userId"], event["userName"], namespace="users")
    else:
        event["userName"] = already_seen

    return [event]


@filter
def is_server(message, _):
    """Select server events."""
    ctx = message["event"]["context"]
    return ctx["resourcePath"] == "/server"
