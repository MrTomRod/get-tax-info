import pytest
from get_tax_info import TaxID, GetTaxInfo, TaxIdNnotFoundError

@pytest.fixture(scope="module")
def gti():
    """Fixture for GetTaxInfo instance."""
    instance = GetTaxInfo()
    yield instance
    instance.close()

class TestTaxID:
    def test_simple_setup(self):
        TaxID(taxid=0, scientific_name='test', unique_name='uniq', parent_taxid=1, rank='rank')

    def test_dynamic_setup(self, gti):
        t = TaxID(taxid=2590146, gti=gti)
        assert t.scientific_name == "Ektaphelenchus kanzakii"

    def test_parent(self, gti):
        t = TaxID(taxid=2590146, gti=gti)
        p = t.parent
        assert p.taxid == 483517

    def test_children(self, gti):
        t = TaxID(taxid=483517, gti=gti)
        children = t.children
        assert len(children) > 0
        for child in children:
            assert isinstance(child.taxid, int)

    def test_rank(self, gti):
        t = TaxID(taxid=2590146, gti=gti)
        r = t.tax_at_rank('genus')
        assert r.rank == 'genus'
        assert r.scientific_name == 'Ektaphelenchus'

    def test_nonexistent_rank(self, gti):
        t = TaxID(taxid=2590146, gti=gti)
        with pytest.raises(KeyError):
            t.tax_at_rank('yolo')

class TestGetTaxInfo:
    def test_get_names_first_entry(self, gti):
        assert gti.get_scientific_name(taxid=1) == "root"

    def test_get_names_last_entry(self, gti):
        assert gti.get_scientific_name(taxid=2590146) == "Ektaphelenchus kanzakii"
        assert gti.get_unique_name(taxid=2590146) == "Ektaphelenchus kanzakii"

    def test_get_names_regular(self, gti):
        assert gti.get_scientific_name(taxid=2) == "Bacteria"
        assert gti.get_unique_name(taxid=2) == "Bacteria <bacteria>"

    def test_get_names_nonexistent_entry(self, gti):
        with pytest.raises(TaxIdNnotFoundError):
            gti.get_scientific_name(taxid=3)
        with pytest.raises(TaxIdNnotFoundError):
            gti.get_unique_name(taxid=3)

    def test_get_parent_and_rank_first_entry(self, gti):
        parent = gti.get_parent(taxid=1)
        rank = gti.get_rank(taxid=1)
        assert parent == 1
        assert rank == "no rank"

    def test_get_parent_and_rank_last_entry(self, gti):
        parent = gti.get_parent(taxid=2590146)
        rank = gti.get_rank(taxid=2590146)
        assert parent == 483517
        assert rank == "species"

    def test_get_parent_and_rank_regular_entry(self, gti):
        parent = gti.get_parent(taxid=2)
        rank = gti.get_rank(taxid=2)
        assert parent == 131567
        assert rank == "domain"

    def test_get_info_first(self, gti):
        taxid, scientific_name, unique_name, parent, rank = gti.get_taxid_values_by_id(taxid=1)
        assert scientific_name == "root"
        assert unique_name == "root"
        assert parent == 1
        assert rank == "no rank"

    def test_get_taxid(self, gti):
        taxid, scientific_name, unique_name, parent, rank = gti.get_taxid_values_by_unique_name(
            "Bacteria <bacteria>")
        assert taxid == 2

    def test_taxid_search(self, gti):
        result = gti.query_taxid_unique_names('porolactobacillus', rank='genus', startswith=False)
        assert result == [(2077, 'Sporolactobacillus', 'Sporolactobacillus', 186821, 'genus')]

    def test_taxid_search_nonexistent(self, gti):
        result = gti.query_taxid_unique_names('porolactobacillus', rank='genus', startswith=True)
        assert result == []
