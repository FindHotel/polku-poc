"""Test creating and deleting and environment."""


from dateutil.parser import parse as parse_datetime
import gzip
import imp
import pytest
import uuid

import analytics
from kinesisutils.kinesisutils import KinesisGenerator


@pytest.mark.parametrize("uid, type, properties, endpoint", [
    [str(uuid.uuid4()), "Signed Up", {"prop1": "value1"}, "/client"],
    [str(uuid.uuid4()), "Booked", {"prop2": "value2"}, "/server"]
    ])
def test_new_user(uid, type, properties, endpoint, api_root, api_key, streams):
    """Test processing a new user."""

    kg_input = KinesisGenerator(streams.input, timeout=5)
    kg_output = KinesisGenerator(streams.output, timeout=10)
    # Cloudwatch logs automatically compresses with GZIP all records before 
    # delivering them to Kinesis.
    kg_log = KinesisGenerator(streams.log, timeout=30,
                               preprocess=gzip.decompress)
    # Forget the current analytics endpoint setting
    imp.reload(analytics)
    analytics.write_key = api_key
    analytics.endpoint = api_root + endpoint
    analytics.track(uid, type, properties)
    recs_input = [rec for rec in kg_input]
    recs_output = [rec for rec in kg_output]

    recs_log = [x for x in _get_log_events(kg_log)
                if x["message"].find("New user") > -1]
    assert len(recs_input) == 1
    assert len(recs_output) == 1
    assert len(recs_log) == 1
    assert "sentAt" in recs_input[0] and "context" in recs_input[0] \
            and "event" in recs_input[0]
    assert parse_datetime(recs_input[0]["sentAt"])
    assert recs_input[0]["event"]["userId"] == uid
    assert "userName" not in recs_input[0] and "user_name" in recs_output[0]


@pytest.mark.parametrize("uid, type, props, endpoint", [
    [str(uuid.uuid4()), "Signed Up", {"prop1": "value1"}, "/server"],
    [str(uuid.uuid4()), "Booked", {"prop2": "value2"}, "/client"]
    ])
def test_seen_user(uid, type, props, endpoint, api_root, api_key, streams):
    """Test processing an already seen user."""

    imp.reload(analytics)
    analytics.write_key = api_key
    analytics.endpoint = api_root + endpoint
    kg_log = KinesisGenerator(streams.log, timeout=30,
                               preprocess=gzip.decompress)
    analytics.track(uid, type, props)
    analytics.track(uid, type, props)
    recs_log = [x for x in _get_log_events(kg_log)
                if x["message"].find("Already seen user") > -1]
    assert len(recs_log) == 1


def _get_log_events(kg_logs):
    """Get log messages from Cloudwatch logs events."""
    msgs = []
    for rec in kg_logs:
        for logev in rec["logEvents"]:
            msgs.append(dict(zip(
                ['level', 'timestamp', 'requestId', 'message'],
                [x.rstrip() for x in logev["message"].split('\t')])))

    return msgs
