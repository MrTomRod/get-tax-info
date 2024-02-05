"""
Input: taxid
Output: busco dataset name
"""
from get_tax_info import UniqueNameNotFoundError
from get_tax_info.GetBusco import GetBusco


def taxid_to_busco_dataset(
        taxid: int,
        busco_download_path: str = None,
        db_path: str = None,
        taxdump_tar: str = None,
        reload_data: bool = False
) -> str:
    """
    :param taxid: int of taxid
    :returns: str of busco dataset name
    """
    gb = GetBusco(
        busco_download_path=busco_download_path,
        db_path=db_path,
        taxdump_tar=taxdump_tar,
        reload_data=reload_data
    )
    ds = gb.get_busco_dataset(taxid)
    return ds


def add_taxid_busco_column(
        csv: str,
        sep: str = '\t',
        header: int = 0,
        species_column: str = 'Species',
        taxid_column: str = 'TaxID',
        busco_column: str = 'BUSCO_dataset',
        busco_download_path: str = None,
        db_path: str = None,
        taxdump_tar: str = None,
        reload_data: bool = False
):
    gb = GetBusco(
        busco_download_path=busco_download_path,
        db_path=db_path,
        taxdump_tar=taxdump_tar,
        reload_data=reload_data
    )

    import pandas as pd

    df = pd.read_csv(csv, delimiter=sep, header=header, index_col=False)

    print(f'Preview:\n{df.head()}\n')

    species_to_taxid_cache = {}

    def species_to_taxid(species):
        if species in species_to_taxid_cache:
            return species_to_taxid_cache[species]
        try:
            t = gb.get_taxid_values_by_unique_name(species)[0]
            species_to_taxid_cache[species] = t
            return t
        except UniqueNameNotFoundError:
            t = int(input(f'Could not find {species} in the database. Please provide the taxid: '))
            species_to_taxid_cache[species] = t
            return t

    if taxid_column not in df.columns:
        assert species_column in df.columns, f'{species_column=} and {taxid_column=} not in {df.columns=}'
        print(f'Adding {taxid_column} column...')
        df[taxid_column] = df[species_column].apply(species_to_taxid)

    df[busco_column] = df[taxid_column].apply(lambda t: gb.get_busco_dataset(t))

    print(f'\nPreview:\n{df.head()}\n')

    df.to_csv(csv + '.addcol', sep=sep, index=False)

    print(f'Wrote {csv}.addcol')


def main():
    from fire import Fire

    Fire({
        'taxid-to-busco-dataset': taxid_to_busco_dataset,
        'add-taxid-column': add_taxid_busco_column
    })


if __name__ == '__main__':
    main()
