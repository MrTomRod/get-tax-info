import os
from dataclasses import dataclass
from typing import Optional

import platformdirs


@dataclass(frozen=True)
class AppConfig:
    """Resolved storage/input paths for get-tax-info resources."""

    cache_dir: str
    db_path: str
    busco_json_path: str
    busco_download_path: str
    taxdump_tar: Optional[str] = None

    @classmethod
    def from_sources(
        cls,
        *,
        cache_dir: Optional[str] = None,
        db_path: Optional[str] = None,
        busco_json_path: Optional[str] = None,
        busco_download_path: Optional[str] = None,
        taxdump_tar: Optional[str] = None,
    ) -> "AppConfig":
        """Resolve configuration with precedence: explicit args > env vars > defaults."""
        resolved_cache_dir = os.path.expanduser(
            cache_dir
            or os.environ.get("GET_TAX_INFO_CACHE_DIR")
            or platformdirs.user_cache_dir("get-tax-info")
        )

        resolved_db_path = os.path.expanduser(
            db_path
            or os.environ.get("GET_TAX_INFO_DB")
            or os.path.join(resolved_cache_dir, "taxdump.db")
        )

        resolved_busco_json_path = os.path.expanduser(
            busco_json_path
            or os.environ.get("GET_TAX_INFO_BUSCO_JSON")
            or os.path.join(resolved_cache_dir, "busco_datasets.json")
        )

        resolved_busco_download_path = os.path.expanduser(
            busco_download_path
            or os.environ.get("GET_TAX_INFO_BUSCO_DOWNLOADS")
            or os.environ.get("BUSCO_DOWNLOAD_PATH")
            or "busco_downloads"
        )

        resolved_taxdump_tar = taxdump_tar or os.environ.get("GET_TAX_INFO_TAXDUMP_TAR")
        if resolved_taxdump_tar:
            resolved_taxdump_tar = os.path.expanduser(resolved_taxdump_tar)

        return cls(
            cache_dir=resolved_cache_dir,
            db_path=resolved_db_path,
            busco_json_path=resolved_busco_json_path,
            busco_download_path=resolved_busco_download_path,
            taxdump_tar=resolved_taxdump_tar,
        )

    def ensure_directories(self) -> None:
        """Create required parent directories for cache-backed files."""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.busco_json_path), exist_ok=True)

    def with_overrides(
        self,
        *,
        cache_dir: Optional[str] = None,
        db_path: Optional[str] = None,
        busco_json_path: Optional[str] = None,
        busco_download_path: Optional[str] = None,
        taxdump_tar: Optional[str] = None,
    ) -> "AppConfig":
        """Return a new config that keeps existing values unless explicitly overridden."""
        return AppConfig.from_sources(
            cache_dir=cache_dir or self.cache_dir,
            db_path=db_path or self.db_path,
            busco_json_path=busco_json_path or self.busco_json_path,
            busco_download_path=busco_download_path or self.busco_download_path,
            taxdump_tar=taxdump_tar if taxdump_tar is not None else self.taxdump_tar,
        )


def resolve_config(
    config: Optional[AppConfig] = None,
    *,
    cache_dir: Optional[str] = None,
    db_path: Optional[str] = None,
    busco_json_path: Optional[str] = None,
    busco_download_path: Optional[str] = None,
    taxdump_tar: Optional[str] = None,
) -> AppConfig:
    """Return an AppConfig from explicit overrides and/or an existing config."""
    if config is None:
        return AppConfig.from_sources(
            cache_dir=cache_dir,
            db_path=db_path,
            busco_json_path=busco_json_path,
            busco_download_path=busco_download_path,
            taxdump_tar=taxdump_tar,
        )

    return config.with_overrides(
        cache_dir=cache_dir,
        db_path=db_path,
        busco_json_path=busco_json_path,
        busco_download_path=busco_download_path,
        taxdump_tar=taxdump_tar,
    )


