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

For BUSCO, the TaxID is used to determine the best BUSCO dataset. This is done by finding the most recent ancestor of 
the TaxID that has a BUSCO dataset. The data is taken from an existing BUSCO installation. Run the following command to
get the BUSCO datasets:

```bash
BUSCO_DOWNLOAD_PATH=/path/to/busco_downloads
# Download the BUSCO datasets
busco --download prokaryota --download_path $BUSCO_DOWNLOAD_PATH
# Update the cache based on the downloaded lineages
get-tax-info taxid_to_busco_dataset --taxid 110 --busco_download_path $BUSCO_DOWNLOAD_PATH
``` 


## Setup:

```bash
pip install git+https://github.com/MrTomRod/get-tax-info
```

```python3
from get_tax_info import TaxID, GetTaxInfo

# this will automatically download the data from NCBI
gti = GetTaxInfo()

# this will import a local file, or download the taxdump there
gti = GetTaxInfo(db_path='~/.cache/get-tax-info.db')

# this will import a local file, or download the taxdump there
gti = GetTaxInfo(taxdump_tar='/path/to/taxdump.tar.gz')

# the argument reload_data will force a re-import
gti = GetTaxInfo(reload_data=True)

```

## Usage:

```bash
$ get-tax-info taxid_to_busco_dataset --taxid 110
rhizobiales_odb10

$ get-tax-info add_taxid_column table.tsv --sep ,
Preview:
Identifier         Barcode                     Species
0  SAMPLE1  bc2041--bc2041  Streptococcus thermophilus
1  SAMPLE2  bc2042--bc2042  Streptococcus thermophilus
2  SAMPLE3  bc2043--bc2043   Leuconostoc mesenteroides
3  SAMPLE4  bc2044--bc2044             Pseudomonas sp.
4  SAMPLE5  bc2045--bc2045             Clostridium sp.

Adding TaxID column...
Could not find Bacillus sp. in the database. Please provide the taxid: 1409

Preview:
Identifier         Barcode                     Species  TaxID          BUSCO_dataset
0  SAMPLE1  bc2041--bc2041  Streptococcus thermophilus   1308  lactobacillales_odb10
1  SAMPLE2  bc2042--bc2042  Streptococcus thermophilus   1308  lactobacillales_odb10
2  SAMPLE3  bc2043--bc2043   Leuconostoc mesenteroides   1245  lactobacillales_odb10
3  SAMPLE4  bc2044--bc2044             Pseudomonas sp.   306   pseudomonadales_odb10
4  SAMPLE5  bc2045--bc2045             Clostridium sp.   1506    clostridiales_odb10

Wrote table.tsv.addcol
```

```python3
# load class
from get_tax_info import TaxID, GetBusco

gti = GetBusco()
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
gti.get_busco_dataset(1597)  # lactobacillales_odb10
```