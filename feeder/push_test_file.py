"""Push one timestamped JSON file into the landing Volume (Phase 0, Session 4).

This proves the feeder path from PRD decision D1: something outside the workspace
(GitHub Actions) authenticates as courtiq-cicd and writes a file into the Volume
through the Files API. Phase 3's live-score feeder reuses exactly this route.

Rules it follows (technical design, section 3.5):
  * files are immutable: a new UTC-timestamped name every run, never overwritten
  * any error exits non-zero and writes nothing else

Usage:
  As yourself:   $env:DATABRICKS_CONFIG_PROFILE = "courtiq"; uv run python -m feeder.push_test_file
  In Actions:    DATABRICKS_HOST / CLIENT_ID / CLIENT_SECRET set from GitHub secrets
"""

from __future__ import annotations

import io
import json
import os
import sys
from datetime import UTC, datetime

from databricks.sdk import WorkspaceClient

from courtiq.config import Settings

FOLDER = "_feeder_test"


def target_path(settings: Settings, now: datetime) -> str:
    """Immutable, sortable file name, e.g. .../_feeder_test/20261028T143005123456Z.json."""
    return f"{settings.landing_path}/{FOLDER}/{now.strftime('%Y%m%dT%H%M%S%fZ')}.json"


def build_payload(now: datetime, writer: str, environ: dict[str, str]) -> dict[str, str | None]:
    return {
        "source": "feeder_test",
        "written_at": now.isoformat(),
        "writer": writer,
        "github_run_id": environ.get("GITHUB_RUN_ID"),
        "github_sha": environ.get("GITHUB_SHA"),
    }


def push(w: WorkspaceClient, path: str, payload: dict[str, str | None]) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    # overwrite=False: if the name somehow exists, fail rather than replace a landed file.
    w.files.upload(path, io.BytesIO(body), overwrite=False)


def main() -> int:
    settings = Settings.from_env()
    w = WorkspaceClient()
    me = w.current_user.me()
    writer = me.display_name or me.user_name or "unknown"
    now = datetime.now(UTC)
    path = target_path(settings, now)
    push(w, path, build_payload(now, writer, dict(os.environ)))
    print(f"wrote {path} as {writer}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
