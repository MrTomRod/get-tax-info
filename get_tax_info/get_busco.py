#
import json
import os.path

from .get_tax_info import GetTaxInfo, platformdirs
from .tax_id import TaxID
from .utils import BuscoParentNotFoundError, ROOT, UniqueNameNotFoundError, query_options

"""
Can also find the best BUSCO (busco.ezlab.org) dataset for a given taxid.
"""


def load_lineages_to_json(out_json: str, busco_download_path: str = 'busco_downloads'):
    """
    Creates a json file with the lineage of all BUSCO datasets.
    Before running this function, download the BUSCO datasets with:
    $ busco --download prokaryota --download_path busco_downloads

    :param out_json: path to the output json file
    :param busco_download_path: path to the BUSCO datasets
    """

    assert os.path.isdir(busco_download_path), f'''
    {busco_download_path=} does not exist. Please download the BUSCO datasets first, e.g.:
    $ busco --download prokaryota --download_path busco_downloads
    '''

    def extract_taxid(lineage):
        # Try dataset.cfg first (BUSCO 6 / odb12)
        cfg_path = os.path.join(busco_download_path, 'lineages', lineage, 'dataset.cfg')
        if os.path.isfile(cfg_path):
            with open(cfg_path) as f:
                for line in f:
                    if line.startswith('ncbi_taxid='):
                        return int(line.split('=')[1].strip())

        # Fallback to HMM filename parsing
        hmm_dir = os.path.join(busco_download_path, 'lineages', lineage, 'hmms')
        if os.path.isdir(hmm_dir):
            hmms = os.listdir(hmm_dir)
            if hmms:
                hmm_file = hmms[0]
                if 'at' in hmm_file:
                    return int(hmm_file.split('at')[1].split('.')[0])
        return None

    busco_dataset = {}
    for lineage in os.listdir(os.path.join(busco_download_path, 'lineages')):
        taxid = extract_taxid(lineage)
        if taxid is not None:
            busco_dataset[taxid] = lineage

    print(f'Loaded {len(busco_dataset)} BUSCO datasets.')

    with open(out_json, 'w') as f:
        json.dump(busco_dataset, f, indent=4)


class GetBusco(GetTaxInfo):
    busco_dataset: {int: str}
    _busco_datasets_json = None

    def __init__(self, *args, busco_download_path: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        if self._busco_datasets_json is None:
            cache_dir = platformdirs.user_cache_dir('get-tax-info')
            self._busco_datasets_json = os.path.join(cache_dir, 'busco_datasets.json')

        reload_data = kwargs.get('reload_data', False)
        if not os.path.isfile(self._busco_datasets_json) or reload_data:
            if busco_download_path is None:
                busco_download_path = os.environ.get('BUSCO_DOWNLOAD_PATH', 'busco_downloads')
            load_lineages_to_json(self._busco_datasets_json, busco_download_path)

        with open(self._busco_datasets_json) as f:
            self.busco_dataset = json.load(f)
        # convert keys to int
        self.busco_dataset = {int(k): v for k, v in self.busco_dataset.items()}

    def get_busco_dataset(self, taxid: int) -> str:
        """:returns: tuple(filename, title) of the best BUSCO dataset or :raises: TaxIdNnotFoundError"""
        orig_taxid = taxid
        while taxid not in self.busco_dataset and taxid != 1:
            taxid = self.get_parent(taxid)

        if taxid not in self.busco_dataset:
            raise BuscoParentNotFoundError(f'TaxID {orig_taxid} has no BUSCO-parent! (Travedled to root-node.)')

        return self.busco_dataset[taxid]
