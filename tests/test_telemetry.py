import json
import tempfile
import unittest
from pathlib import Path

from generative_glados.telemetry import EventStream, MAX_LINE, PREFIX, parse_line, read_events


def observation(**updates):
    result = {
        "schema_version": 1, "origin": "synthetic", "event": "laser_powered",
        "map": "sp_a2_laser_intro", "run_id": "synthetic-fixture", "seq": 1,
        "game_time": 12.5,
        "data": {"target": "catcher_1", "powered": True, "laser_hook": True},
    }
    result.update(updates)
    return result


def line(**updates):
    return PREFIX + json.dumps(observation(**updates)).encode() + b"\n"


class TelemetryTests(unittest.TestCase):
    def test_valid_event_is_explicitly_synthetic(self):
        self.assertEqual(parse_line(line())["origin"], "synthetic")

    def test_console_noise_and_command_echo_are_not_events(self):
        for raw in [b"ordinary game log\n", b"] echo " + line(), b"prefix " + line()]:
            self.assertIsNone(parse_line(raw))

    def test_partial_record_waits_for_newline(self):
        stream = EventStream()
        raw = line()
        self.assertEqual(list(stream.feed(raw[:-1])), [])
        self.assertEqual(len(list(stream.feed(raw[-1:]))), 1)

    def test_arbitrary_chunk_boundaries_and_crlf(self):
        raw = (b"noise\r\n" + line().replace(b"\n", b"\r\n")) * 2
        stream = EventStream()
        events = []
        for byte in raw:
            events.extend(stream.feed(bytes([byte])))
        self.assertEqual(len(events), 2)

    def test_malformed_record_does_not_poison_next_record(self):
        stream = EventStream()
        events = list(stream.feed(PREFIX + b"{broken}\n" + line()))
        self.assertEqual(len(events), 1)
        self.assertEqual(stream.rejected, 1)

    def test_oversized_record_is_dropped_with_bounded_buffer(self):
        stream = EventStream()
        self.assertEqual(list(stream.feed(b"x" * (MAX_LINE + 1))), [])
        self.assertLessEqual(len(stream.buffer), MAX_LINE)
        self.assertEqual(len(list(stream.feed(b"tail\n" + line()))), 1)
        self.assertEqual(stream.rejected, 1)

    def test_invalid_envelope_values_are_rejected(self):
        invalid = [
            {"schema_version": True}, {"schema_version": 2}, {"seq": True}, {"seq": -1},
            {"seq": 1.5}, {"game_time": float("nan")}, {"game_time": -1},
            {"map": "../save/auto"}, {"event": "invented_event"}, {"event": []},
            {"run_id": ""}, {"origin": "unlabelled"},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_line(line(**value))

    def test_missing_extra_and_contradictory_data_rejected(self):
        for data in [None, {}, {"target": "catcher_1", "powered": False, "laser_hook": True},
                     {"target": None, "powered": True, "laser_hook": False}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_line(line(data=data))
        with self.assertRaises(ValueError):
            parse_line(line(unexpected="do not accept executable instructions"))

    def test_invalid_utf8_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_line(PREFIX + b'"\xff"')

    def test_file_read_and_explicit_from_end(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "console.log"
            path.write_bytes(b"game noise\n" + line())
            self.assertEqual(len(list(read_events(path))), 1)
            self.assertEqual(list(read_events(path, from_end=True)), [])
