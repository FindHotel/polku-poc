"""Processing logic."""

import copy
from datetime import datetime
from dateutil.parser import parse as parse_datetime
import json
import logging
import re

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
def name_user(message, ctx):
    """Name all users."""

    event = message["event"]
    # Add also the sentAt and receivedAt timestamps
    event["sentAt"] = message["sentAt"]
    event["receivedAt"] = message["receivedAt"]
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

    return prepare_for_redshift(event, ctx)


@filter
def is_server(message, _):
    """Select server events."""
    ctx = message["context"]
    if ctx["resourcePath"] == "/server":
        logger.info("Identified server event: {}".format(_pretty(message)))
        return True
    return False


@filter
def is_client(message, _):
    """Select client events."""
    ctx = message["context"]
    if ctx["resourcePath"] == "/client":
        logger.info("Identified client event: {}".format(_pretty(message)))
        return True
    return False


@mapper
def notify_slack(message, _):
    """Forward the incoming message to a Slack channel."""
    logger.info(json.dumps(message, indent=4))


@mapper
def extract_log_events(message, ctx):
    """Extract log events from AWS Cloudwatch Logs event."""
    message = camel_to_snake(message)
    log_events = message["log_events"]
    del message["log_events"]
    out = []
    for ev in log_events:
        ev["context"] = copy.deepcopy(message)
        out.append(prepare_for_redshift(ev, ctx))
    return out


@mapper
def prepare_for_redshift(message, _):
    """Gets an event payload ready to be delivered to a Redshift table."""
    message = camel_to_snake(message)
    for ts_field in ["timestamp", "sent_at"]:
        # Convert timestamp to the format Redshift likes
        if ts_field not in message:
            continue
        if isinstance(message[ts_field], str):
            message[ts_field] = parse_datetime(
                message[ts_field]).strftime("%Y-%m-%d %H:%M:%S")
    return flatten(message)


def flatten(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def camel_to_snake(ev):
    """Convert all keys in a nested dict to snake case."""

    out = {}
    for k, v in ev.items():
        if type(v) is dict:
            v = camel_to_snake(v)
        elif type(v) is list:
            for ix, vv in enumerate(v):
                if type(vv) is dict:
                    v[ix] = camel_to_snake(vv)
        out[_camel_to_snake(k)] = v

    return out


def _camel_to_snake(name):
    """Convert string from camelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _pretty(msg):
    """Pretty stringified version of an event."""
    return json.dumps(msg, indent=4)
