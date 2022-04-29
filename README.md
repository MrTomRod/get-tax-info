# get-tax-info

## Idea:

Load the NCBI-provided datafiles `names.dmp` and `nodes.dmp`, into a SQlite database, allowing very quick hash-based
searches.

When the class is initiated for the first time, the NCBI-file has to be downloaded and converted into a SQLite db.
This happens automatically by default, but if the taxdump.tar.gz file has already been downloaded, it can be specified
as a parameter.

By default, the SQlite database will be saved to wherever `get-tax-info` is installed (for example, into the virutal
environment). Alternatively, the desired location of the database can be chosen by setting the environment
variable `GET_TAX_INFO_DB` or by initiating the GetTaxInfo class with the parameter `db_path`.

## Setup:
```bash
pip install 
```

```python3
from get_tax_info import TaxID, GetTaxInfo

# this will automatically download the data from NCBI
gti = GetTaxInfo()

# this will import a local file, or download the taxdump there
gti = GetTaxInfo(db_path='/path/to/sqlite.db')

# this will import a local file, or download the taxdump there
gti = GetTaxInfo(taxdump_tar='/path/to/taxdump.tar.gz')

# the argument reload_data will force a re-import
gti = GetTaxInfo(reload_data=True)

```

## Usage:

```python3
# load class
from get_tax_info import TaxID, GetTaxInfo

gti = GetTaxInfo()
TaxID.gti = gti  # Edit TaxID-class: give it a GetTaxInfo-instance

## Use TaxID class (recommended):
t = TaxID(taxid=2590146)  # <TaxID 2590146 (Ektaphelenchus kanzakii)>
t.taxid  # 2590146
p = t.parent  # <TaxID 483517 (Ektaphelenchus)>
p.children  # [<TaxID 483518 (Ektaphelenchus obtusus)>, <TaxID 1226725 (Ektaphelenchus taiwanensis)>, ...]
t.rank  # 'species'
t.scientific_name  # 'Ektaphelenchus kanzakii'
t.unique_name  # 'Ektaphelenchus kanzakii'

## use GetTaxInfo directly
# taxid -> scientific name
gti.get_scientific_name(taxid=2590146)  # Ektaphelenchus kanzakii

# taxid -> rank
gti.get_rank(taxid=2590146)  # "species"

# taxid -> parent taxid
gti.get_parent(taxid=2590146)  # 483517

# taxid -> best BUSCO dataset (arguably not necessary anymore as BUSCO has autodetect mechanism)
# 1597 = Lactobacillus paracasei
gti.get_busco_dataset_filename(1597)  # lactobacillales_odb9.tar.gz
gti.get_busco_dataset_title(1597)  # Lactobacillales
```