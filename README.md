# get-tax-info

Load NCBI taxonomy (`names.dmp` and `nodes.dmp`) into a SQLite database for lightning-fast hash-based lookups.

> [!CAUTION]
> A very similar solution was created by [ete4](https://github.com/etetoolkit/ete4) / [ncbiquery.py](https://github.com/etetoolkit/ete4/blob/ete4/ete4/ncbi_taxonomy/ncbiquery.py) - I suppose most people should use that implementation instead.

## Features
- **Fast**: Indexed SQLite queries for names, parents, and children.
- **Automatic**: Downloads and converts NCBI data on first run.
- **Easy Storage**: Uses standard user cache directories by default.
- **BUSCO Integration**: Maps TaxIDs to the best BUSCO dataset for lineage analysis.

## Installation
```bash
pip install get-tax-info
```

## Configuration
Path resolution uses this precedence:
1. Explicit constructor arguments (or `AppConfig` fields)
2. Environment variables
3. `platformdirs.user_cache_dir("get-tax-info")` defaults

Default cache locations (Linux example):
- DB: `~/.cache/get-tax-info/taxdump.db`
- BUSCO json: `~/.cache/get-tax-info/busco_datasets.json`

Supported environment variables:
- `GET_TAX_INFO_CACHE_DIR`
- `GET_TAX_INFO_DB`
- `GET_TAX_INFO_BUSCO_JSON`
- `GET_TAX_INFO_BUSCO_DOWNLOADS`
- `GET_TAX_INFO_TAXDUMP_TAR`

Legacy fallback still supported for BUSCO downloads:
- `BUSCO_DOWNLOAD_PATH`

Programmatic config for embedded usage:

```python
from get_tax_info import AppConfig, GetTaxInfo, GetBusco

cfg = AppConfig.from_sources(
	cache_dir="/data/get-tax-info",
	busco_download_path="/data/busco_downloads",
)

gti = GetTaxInfo(config=cfg)
gb = GetBusco(config=cfg)
```

## Python Usage
```python
from get_tax_info import GetTaxInfo, TaxID

# Automatically download/init data on first use
gti = GetTaxInfo()

# Use the TaxID object (recommended)
t = gti.get_taxid_object(2590146)  # Ektaphelenchus kanzakii
print(t.scientific_name, t.rank)   # 'Ektaphelenchus kanzakii', 'species'

# Parents and children
parent = t.parent                  # <TaxID 483517 (Ektaphelenchus)>
children = parent.children          # List of TaxID objects

# Ancestor at specific rank
genus = t.tax_at_rank('genus')
```

## CLI Usage
```bash
# Print effective resolved paths (useful in Docker/CI debugging)
get-tax-info show-config

# Get BUSCO dataset for a TaxID
get-tax-info taxid-to-busco-dataset --taxid 110

# Override cache/json paths explicitly (CLI args > env vars > defaults)
get-tax-info taxid-to-busco-dataset \
  --taxid 1597 \
  --cache_dir /data/get-tax-info \
  --busco_json_path /data/get-tax-info/busco_datasets.json \
  --busco_download_path /data/busco_downloads

# Add TaxID and BUSCO column to a CSV/TSV table
get-tax-info add-taxid-column table.tsv --sep ,
```

A complete demonstration of the BUSCO workflow (including Podman usage) can be found in [demo_busco_workflow.sh](demo_busco_workflow.sh).

---
*Note: BUSCO dataset mapping requires pre-downloaded lineages. See [get_busco.py](get_tax_info/get_busco.py) for details.*
