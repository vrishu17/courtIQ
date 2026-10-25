"""Runtime configuration for CourtIQ jobs and the app.

Every environment-specific value arrives as an environment variable, set by the
bundle (job parameters, app env vars). Code never hard-codes a catalog or host.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

VALID_ENVS = {"dev", "prod", "trial"}
VALID_INGEST_MODES = {"upload", "feeder", "direct"}


@dataclass(frozen=True)
class Settings:
    env: str
    catalog: str
    ingest_mode: str
    lakebase_branch: str

    @property
    def landing_path(self) -> str:
        """Root of the landing Volume: the ingestion contract (ADR-01)."""
        return f"/Volumes/{self.catalog}/landing/raw"

    def table(self, schema: str, name: str) -> str:
        """Fully qualified three-part table name."""
        return f"{self.catalog}.{schema}.{name}"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        e = os.environ if environ is None else environ
        settings = cls(
            env=e.get("COURTIQ_ENV", "dev"),
            catalog=e.get("COURTIQ_CATALOG", "courtiq_dev"),
            ingest_mode=e.get("COURTIQ_INGEST_MODE", "upload"),
            lakebase_branch=e.get("COURTIQ_LAKEBASE_BRANCH", "dev"),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.env not in VALID_ENVS:
            raise ValueError(f"Unknown env {self.env!r}; expected one of {sorted(VALID_ENVS)}")
        if self.ingest_mode not in VALID_INGEST_MODES:
            raise ValueError(
                f"Unknown ingest_mode {self.ingest_mode!r}; "
                f"expected one of {sorted(VALID_INGEST_MODES)}"
            )
