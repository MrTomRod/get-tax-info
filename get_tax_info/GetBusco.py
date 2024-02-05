#
import json
import os.path

from .GetTaxInfo import GetTaxInfo
from .TaxID import TaxID
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
        hmm_file = os.listdir(f'{busco_download_path}/lineages/{lineage}/hmms')[0]  # e.g. 26885at28221.hmm -> lineage taxid is 28221
        return int(hmm_file.split('at')[1].split('.')[0])

    busco_dataset = {extract_taxid(lineage): lineage for lineage in os.listdir(f'{busco_download_path}/lineages')}

    print('Loaded {len(busco_dataset)} BUSCO datasets.')

    with open(out_json, 'w') as f:
        json.dump(busco_dataset, f, indent=4)


class GetBusco(GetTaxInfo):
    busco_dataset: {int: str}
    _busco_datasets_json = f'{ROOT}/data/busco_datasets.json'

    def __init__(self, *args, busco_download_path: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        TaxID.gti = self

        if not os.path.isfile(self._busco_datasets_json):
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
