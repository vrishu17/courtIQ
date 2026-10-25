import pytest

from courtiq.config import Settings


def test_defaults_point_to_dev():
    s = Settings.from_env({})
    assert s.env == "dev"
    assert s.catalog == "courtiq_dev"
    assert s.landing_path == "/Volumes/courtiq_dev/landing/raw"


def test_prod_values_are_read_from_environment():
    s = Settings.from_env(
        {"COURTIQ_ENV": "prod", "COURTIQ_CATALOG": "courtiq_prod", "COURTIQ_INGEST_MODE": "feeder"}
    )
    assert s.table("silver", "fact_point") == "courtiq_prod.silver.fact_point"


def test_unknown_ingest_mode_is_rejected():
    with pytest.raises(ValueError, match="ingest_mode"):
        Settings.from_env({"COURTIQ_INGEST_MODE": "ftp"})
