import pytest
from get_tax_info import GetBusco, TaxIdNnotFoundError, BuscoParentNotFoundError

@pytest.fixture(scope="module")
def gb():
    """Fixture for GetBusco instance with mocked datasets."""
    instance = GetBusco()
    # Mocking the dataset mapping so tests are independent of local cache
    instance.busco_dataset = {
        2: "bacteria_odb10",
        186826: "lactobacillales_odb10"
    }
    yield instance
    instance.close()

class TestGetBusco:
    def test_get_busco_dataset(self, gb):
        # Lactobacillus paracasei
        assert gb.get_busco_dataset(1597) == "lactobacillales_odb10"

    def test_get_busco_dataset_nonexistent_taxid(self, gb):
        # nonexistent taxid: 3
        with pytest.raises(TaxIdNnotFoundError):
            gb.get_busco_dataset(3)

    def test_get_busco_dataset_nonexistent_busco_parent(self, gb):
        # root-node has no busco-parent: 1
        with pytest.raises(BuscoParentNotFoundError):
            gb.get_busco_dataset(1)
