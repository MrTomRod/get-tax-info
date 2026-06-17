from get_tax_info.utils import UniqueNameNotFoundError
from get_tax_info.get_tax_info import GetTaxInfo
from get_tax_info.get_busco import GetBusco
from get_tax_info.config import resolve_config


def show_config(
        cache_dir: str = None,
        db_path: str = None,
        busco_json_path: str = None,
        busco_download_path: str = None,
        taxdump_tar: str = None,
) -> dict:
    """Return the resolved config paths (after applying precedence rules)."""
    config = resolve_config(
        cache_dir=cache_dir,
        db_path=db_path,
        busco_json_path=busco_json_path,
        busco_download_path=busco_download_path,
        taxdump_tar=taxdump_tar,
    )
    return {
        'cache_dir': config.cache_dir,
        'db_path': config.db_path,
        'busco_json_path': config.busco_json_path,
        'busco_download_path': config.busco_download_path,
        'taxdump_tar': config.taxdump_tar,
    }


def init(
        cache_dir: str = None,
        db_path: str = None,
        busco_json_path: str = None,
        taxdump_tar: str = None,
        reload_data: bool = False
) -> str:
    """
    :param taxid: int of taxid
    :returns: str of busco dataset name
    """
    config = resolve_config(
        cache_dir=cache_dir,
        db_path=db_path,
        busco_json_path=busco_json_path,
        taxdump_tar=taxdump_tar,
    )

    gt = GetTaxInfo(
        reload_data=reload_data,
        config=config
    )
    return 'Done!'


def taxid_to_busco_dataset(
        taxid: int,
        cache_dir: str = None,
        busco_download_path: str = None,
        db_path: str = None,
        busco_json_path: str = None,
        taxdump_tar: str = None,
        reload_data: bool = False
) -> str:
    """
    :param taxid: int of taxid
    :returns: str of busco dataset name
    """
    config = resolve_config(
        cache_dir=cache_dir,
        db_path=db_path,
        busco_json_path=busco_json_path,
        busco_download_path=busco_download_path,
        taxdump_tar=taxdump_tar,
    )

    gb = GetBusco(
        reload_data=reload_data,
        config=config
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
        cache_dir: str = None,
        busco_download_path: str = None,
        db_path: str = None,
        busco_json_path: str = None,
        taxdump_tar: str = None,
        reload_data: bool = False
):
    config = resolve_config(
        cache_dir=cache_dir,
        db_path=db_path,
        busco_json_path=busco_json_path,
        busco_download_path=busco_download_path,
        taxdump_tar=taxdump_tar,
    )

    gb = GetBusco(
        reload_data=reload_data,
        config=config
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

    if species_column not in df.columns:
        assert taxid_column in df.columns, f'{species_column=} and {taxid_column=} not in {df.columns=}'
        print(f'Adding {species_column} column...')
        df[species_column] = df[taxid_column].apply(lambda t: gb.get_taxid_values_by_id(t)[1])
    
    print(taxid_column, list(df[taxid_column]))
    df[busco_column] = df[taxid_column].apply(lambda t: gb.get_busco_dataset(t))

    print(f'\nPreview:\n{df.head()}\n')

    input('Press Enter to write to file...')

    df.to_csv(csv + '.addcol', sep=sep, index=False)

    print(f'Wrote {csv}.addcol')


def add_identifier_column(
        ogb_folder_structure: str,
        csv: str,
        sep: str = '\t',
        format: str = '{name}-{i}',
        name_column: str = 'BioSample',
        identifier_column: str = 'Identifier',
):
    import os
    import glob
    import pandas as pd

    df = pd.read_csv(csv, delimiter=sep, index_col=False)

    print(f'Preview:\n{df.head()}\n')

    print('Loading all identifiers...')
    all_identifiers = set(
        os.path.basename(f) for f in glob.glob(f'{ogb_folder_structure}/organisms/*/genomes/*')
    )
    print(len(all_identifiers))
    print(list(all_identifiers)[:10])

    # Add identifier column
    def get_identifier(name):
        for i in range(1, 1000):
            identifier = format.format(name=name, i=i)
            if identifier not in all_identifiers:
                all_identifiers.add(identifier)
                return identifier
        raise ValueError(f'Could not find a unique identifier for {name}')

    df[identifier_column] = df[name_column].apply(get_identifier)

    print(f'\nPreview:\n{df.head()}\n')

    input('Press Enter to write to file...')

    df.to_csv(csv + '.addcol', sep=sep, index=False)

    print(f'Wrote {csv}.addcol')


def main():
    from fire import Fire

    Fire({
        'init': init,
        'taxid-to-busco-dataset': taxid_to_busco_dataset,
        'add-taxid-column': add_taxid_busco_column,
        'add-identifier-column': add_identifier_column,
        'show-config': show_config
    })


if __name__ == '__main__':
    main()
