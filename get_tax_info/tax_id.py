from functools import cached_property


class TaxID:
    """
    TaxID objects represent a NCBI TaxID.

    A TaxID contains the following values:
        taxid, scientific_name, unique_name, rank, parent_taxid

    A TaxID contains the following properties:
        parent -> TaxID object of parent_taxid
        children -> list of children TaxID objects

    A TaxID has the following functions:
        tax_at_rank(rank) -> TaxID object of ancestor who has given rank
    """

    def __init__(
            self, taxid: int = None,
            scientific_name: str = None,
            unique_name: str = None,
            parent_taxid: int = None,
            rank: str = None,
            gti=None
    ):
        if gti is not None:
            self.gti = gti

        if None in [taxid, scientific_name, unique_name, parent_taxid, rank]:
            if taxid is not None:
                taxid, scientific_name, unique_name, parent_taxid, rank = self.gti.get_taxid_values_by_id(taxid)
            elif unique_name is not None:
                taxid, scientific_name, unique_name, parent, rank = self.gti.get_taxid_values_by_unique_name(
                    unique_name)
            else:
                raise AssertionError('To create a TaxID object, provide a taxid or a unique name.')

        self.taxid = taxid
        self.scientific_name = scientific_name
        self.unique_name = unique_name
        self.parent_taxid = parent_taxid
        self.rank = rank

    @property
    def parent(self):
        """:returns: TaxID of parent"""
        if self.taxid == 1:
            return None
        else:
            return TaxID(taxid=self.parent_taxid, gti=self.gti)

    @cached_property
    def depth(self) -> int:
        """:returns: int of depth in taxonomy"""
        if self.taxid == 1:
            return 0
        else:
            return self.parent.depth + 1

    @property
    def children(self) -> list:
        """:returns: list of children's TaxIDs"""
        return [TaxID(*taxid, gti=self.gti) for taxid in self.gti.get_children_by_id(self.taxid)]

    def tax_at_rank(self, rank: str):
        """:returns: TaxID of ancestor with :param rank"""
        taxid = self
        while taxid:
            if taxid.rank == rank:
                return taxid
            taxid = taxid.parent
        raise KeyError(F'Taxid {self.taxid} does not have an ancestor of rank={rank}')

    def __str__(self):
        return F'<TaxID {self.taxid} ({self.scientific_name})>'

    def __repr__(self):
        return F'<TaxID {self.taxid} ({self.unique_name})>'

    def __eq__(self, other):
        return self.taxid == other.taxid
