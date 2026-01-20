# get-tax-info

Load NCBI taxonomy (`names.dmp` and `nodes.dmp`) into a SQLite database for lightning-fast hash-based lookups.

## Features
- **Fast**: Indexed SQLite queries for names, parents, and children.
- **Automatic**: Downloads and converts NCBI data on first run.
- **Easy Storage**: Uses standard user cache directories by default.
- **BUSCO Integration**: Maps TaxIDs to the best BUSCO dataset for lineage analysis.

## Installation
```bash
pip install git+https://github.com/MrTomRod/get-tax-info
```

## Configuration
By default, the database is stored in the user cache directory (e.g., `~/.cache/get-tax-info/`).
- Change location: Set `GET_TAX_INFO_DB` environment variable or pass `db_path` to `GetTaxInfo`.

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
# Get BUSCO dataset for a TaxID
get-tax-info taxid-to-busco-dataset --taxid 110

# Add TaxID and BUSCO column to a CSV/TSV table
get-tax-info add-taxid-column table.tsv --sep ,
```

A complete demonstration of the BUSCO workflow (including Podman usage) can be found in [demo_busco_workflow.sh](demo_busco_workflow.sh).

---
*Note: BUSCO dataset mapping requires pre-downloaded lineages. See [get_busco.py](get_tax_info/get_busco.py) for details.*
