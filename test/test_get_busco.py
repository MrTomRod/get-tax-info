from unittest import TestCase
from get_tax_info import *
from get_tax_info.GetBusco import load_lineages_to_json
from get_tax_info.utils import ROOT


class TestGetBuscoLoad(TestCase):
    def test_load_busco_data(self):
        load_lineages_to_json(
            out_json=f'{ROOT}/data/busco_datasets.json',
            busco_download_path='/home/thomas/sshfs/data/projects/p446_Dialact_Phoenix/2_analyses/B_pacbio/2024.01.24_assemblies/busco_downloads'
        )


class TestGetBusco(TestCase):
    def setUp(self) -> None:
        self.gb = GetBusco()

    def test_get_busco_dataset(self):
        # Lactobacillus paracasei
        self.assertEqual("lactobacillales_odb10", self.gb.get_busco_dataset(1597))

    def test_get_busco_dataset_nonexistent_taxid(self):
        # nonexistent taxid: 3
        with self.assertRaises(TaxIdNnotFoundError):
            self.gb.get_busco_dataset(3)

    def test_get_busco_dataset_nonexistent_busco_parent(self):
        # root-node has no busco-parent: 1
        with self.assertRaises(BuscoParentNotFoundError):
            self.gb.get_busco_dataset(1)
