import json
from datetime import UTC, datetime

from courtiq.config import Settings
from feeder.push_test_file import build_payload, push, target_path

NOW = datetime(2026, 10, 28, 14, 30, 5, 123456, tzinfo=UTC)


def test_target_path_is_in_the_landing_volume_and_timestamped():
    s = Settings.from_env({"COURTIQ_CATALOG": "courtiq_dev"})
    assert (
        target_path(s, NOW)
        == "/Volumes/courtiq_dev/landing/raw/_feeder_test/20261028T143005123456Z.json"
    )


def test_payload_records_who_and_which_run():
    payload = build_payload(NOW, "courtiq-cicd", {"GITHUB_RUN_ID": "42", "GITHUB_SHA": "abc"})
    assert payload["writer"] == "courtiq-cicd"
    assert payload["github_run_id"] == "42"
    assert payload["written_at"] == "2026-10-28T14:30:05.123456+00:00"


def test_push_never_overwrites():
    calls = []

    class FakeFiles:
        def upload(self, path, contents, overwrite=None):
            calls.append((path, json.loads(contents.read()), overwrite))

    class FakeClient:
        files = FakeFiles()

    push(FakeClient(), "/Volumes/x/landing/raw/_feeder_test/a.json", {"source": "feeder_test"})
    assert calls == [
        ("/Volumes/x/landing/raw/_feeder_test/a.json", {"source": "feeder_test"}, False)
    ]
