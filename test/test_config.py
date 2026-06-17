import os

from get_tax_info.config import AppConfig


def test_from_sources_explicit_values_override_environment(monkeypatch):
    monkeypatch.setenv("GET_TAX_INFO_CACHE_DIR", "/env/cache")
    monkeypatch.setenv("GET_TAX_INFO_DB", "/env/cache/custom.db")
    monkeypatch.setenv("GET_TAX_INFO_BUSCO_JSON", "/env/cache/custom_busco.json")
    monkeypatch.setenv("GET_TAX_INFO_BUSCO_DOWNLOADS", "/env/busco")
    monkeypatch.setenv("GET_TAX_INFO_TAXDUMP_TAR", "/env/taxdump.tar.gz")

    cfg = AppConfig.from_sources(
        cache_dir="~/arg-cache",
        db_path="~/arg-cache/arg.db",
        busco_json_path="~/arg-cache/arg-busco.json",
        busco_download_path="~/arg-busco-downloads",
        taxdump_tar="~/arg-taxdump.tar.gz",
    )

    assert cfg.cache_dir == os.path.expanduser("~/arg-cache")
    assert cfg.db_path == os.path.expanduser("~/arg-cache/arg.db")
    assert cfg.busco_json_path == os.path.expanduser("~/arg-cache/arg-busco.json")
    assert cfg.busco_download_path == os.path.expanduser("~/arg-busco-downloads")
    assert cfg.taxdump_tar == os.path.expanduser("~/arg-taxdump.tar.gz")


def test_from_sources_environment_fallback(monkeypatch):
    monkeypatch.setattr(
        "get_tax_info.config.platformdirs.user_cache_dir",
        lambda _: "/platform/cache",
    )

    monkeypatch.delenv("GET_TAX_INFO_DB", raising=False)
    monkeypatch.delenv("GET_TAX_INFO_BUSCO_JSON", raising=False)
    monkeypatch.delenv("GET_TAX_INFO_BUSCO_DOWNLOADS", raising=False)
    monkeypatch.delenv("GET_TAX_INFO_TAXDUMP_TAR", raising=False)

    monkeypatch.setenv("GET_TAX_INFO_CACHE_DIR", "/env/cache")
    monkeypatch.setenv("BUSCO_DOWNLOAD_PATH", "/legacy/busco")

    cfg = AppConfig.from_sources()

    assert cfg.cache_dir == "/env/cache"
    assert cfg.db_path == "/env/cache/taxdump.db"
    assert cfg.busco_json_path == "/env/cache/busco_datasets.json"
    assert cfg.busco_download_path == "/legacy/busco"
    assert cfg.taxdump_tar is None

