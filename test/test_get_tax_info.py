from unittest import TestCase
from get_tax_info import *


class TestTaxID(TestCase):
    def setUp(self) -> None:
        TaxID.gti = GetTaxInfo()

    def test_simple_setup(self):
        TaxID(taxid=0, scientific_name='test', unique_name='uniq', parent_taxid=1, rank='rank')

    def test_dynamic_setup(self):
        t = TaxID(taxid=2590146)
        self.assertEqual("Ektaphelenchus kanzakii", t.scientific_name)

    def test_parent(self):
        t = TaxID(taxid=2590146)
        p = t.parent
        self.assertEqual(483517, p.taxid)

    def test_children(self):
        t = TaxID(taxid=483517)
        children = t.children
        self.assertTrue(len(children) > 0)
        for child in children:
            self.assertTrue(type(child.taxid) is int)

    def test_rank(self):
        t = TaxID(taxid=2590146)
        r = t.tax_at_rank('genus')
        self.assertEqual('genus', r.rank)
        self.assertEqual('Ektaphelenchus', r.scientific_name)

    def test_nonexistent_rank(self):
        t = TaxID(taxid=2590146)
        with self.assertRaises(KeyError):
            r = t.tax_at_rank('yolo')


class TestGetTaxInfo(TestCase):
    def setUp(self) -> None:
        self.gt = GetTaxInfo()
        # self.gt = GetTaxInfo(taxdump_tar='../data/taxdump.tar.gz')

    def tearDown(self) -> None:
        pass

    # test names
    def test_get_names_first_entry(self):
        self.assertEqual("root", self.gt.get_scientific_name(taxid=1))

    def test_get_names_last_entry(self):
        self.assertEqual("Ektaphelenchus kanzakii", self.gt.get_scientific_name(taxid=2590146))
        self.assertEqual("Ektaphelenchus kanzakii", self.gt.get_unique_name(taxid=2590146))

    def test_get_names_regular(self):
        self.assertEqual("Bacteria", self.gt.get_scientific_name(taxid=2))
        self.assertEqual("Bacteria <bacteria>", self.gt.get_unique_name(taxid=2))

    def test_get_names_nonexistent_entry(self):
        with self.assertRaises(TaxIdNnotFoundError):
            self.gt.get_scientific_name(taxid=3)
        with self.assertRaises(TaxIdNnotFoundError):
            self.gt.get_unique_name(taxid=3)

    # test parent and rank
    def test_get_parent_and_rank_first_entry(self):
        parent = self.gt.get_parent(taxid=1)
        rank = self.gt.get_rank(taxid=1)
        self.assertEqual(1, parent)
        self.assertEqual("no rank", rank)

    def test_get_parent_and_rank_last_entry(self):
        parent = self.gt.get_parent(taxid=2590146)
        rank = self.gt.get_rank(taxid=2590146)
        self.assertEqual(483517, parent)
        self.assertEqual("species", rank)

    def test_get_parent_and_rank_regular_entry(self):
        parent = self.gt.get_parent(taxid=2)
        rank = self.gt.get_rank(taxid=2)
        self.assertEqual(131567, parent)
        self.assertEqual("superkingdom", rank)

    # test get_info()
    def test_get_info_first(self):
        taxid, scientific_name, unique_name, parent, rank = self.gt.get_taxid_values_by_id(taxid=1)
        self.assertEqual("root", scientific_name)
        self.assertEqual("root", unique_name)
        self.assertEqual(1, parent)
        self.assertEqual("no rank", rank)

    def test_get_taxid(self):
        taxid, scientific_name, unique_name, parent, rank = self.gt.get_taxid_values_by_unique_name(
            "Bacteria <bacteria>")
        self.assertEqual((2), taxid)

    def test_taxid_search(self):
        result = self.gt.query_taxid_unique_names('porolactobacillus', rank='genus', startswith=False)
        self.assertEqual([(2077, 'Sporolactobacillus', 'Sporolactobacillus', 186821, 'genus')], result)

    def test_taxid_search_nonexistent(self):
        # this function doesn't throw an error but returns an empty list
        result = self.gt.query_taxid_unique_names('porolactobacillus', rank='genus', startswith=True)
        self.assertEqual([], result)
