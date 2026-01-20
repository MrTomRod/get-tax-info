import os
import sqlite3
import platformdirs
from .tax_id import TaxID
from .utils import ROOT, TaxIdNnotFoundError, UniqueNameNotFoundError, NameNotFoundError


class GetTaxInfo:
    """
    Get information about NCBI TaxIDs from names.dmp and nodes.dmp.

    These text files are downloaded on first use and converted into a SQLite-database for efficient lookups.

    Layout of the database:
    --------------
    taxid : int - primary key, unique
        e.g. 2590146 or 2
    scientific_name : str
        e.g. "Ektaphelenchus kanzakii" or "Bacteria"
    unique_name : str - unique
        e.g. "Ektaphelenchus kanzakii" or "Bacteria <bacteria>"
    rank : str
        taxonomic rank (e.g. "species")
    parent : int
        TaxID of parent in taxonomic tree
    """

    def __init__(self, db_path: str = None, taxdump_tar: str = None, reload_data: bool = False):
        if db_path is None:
            cache_dir = platformdirs.user_cache_dir('get-tax-info')
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.environ.get('GET_TAX_INFO_DB', os.path.join(cache_dir, 'taxdump.db'))
        self.sqlite_db = os.path.expanduser(db_path)

            
        if reload_data or not os.path.isfile(self.sqlite_db):
            if taxdump_tar:
                self.update_ncbi_taxonomy_from_file(taxdump_tar)
            else:
                self.update_ncbi_taxonomy_from_web()

        self.conn = sqlite3.connect(self.sqlite_db, uri=True, check_same_thread=False)
        self.db = self.conn.cursor()  # self.db is the cursor for backwards compatibility

    def get_taxid_object(self, taxid: int):
        return TaxID(taxid=taxid, gti=self)

    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def __del__(self):
        self.close()

    def get_children_by_id(self, parent_taxid, size=None) -> [(int, str, str, int, str)]:
        """
        Returns children of a given taxid. Returns list of results.

        :param parent_taxid: taxid whose children should be returned
        :param size: number of results to be returned. default: return all children
        :returns: list of tuples: [(taxid, scientific_name, unique_name, parent, rank), ...]
        """
        self.db.execute('''
            SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids
            WHERE parent IS ?
            ORDER BY taxid
        ''', (parent_taxid,))

        if size:
            taxids = self.db.fetchmany(size=size)
        else:
            taxids = self.db.fetchall()

        if not taxids:
            return []

        return taxids

    def get_taxid_values_by_unique_name(self, unique_name: str) -> (int, str, str, int, str):
        """
        Return taxids that corresponds to a specific unique_name. Returns list of results.
        Ignores upper/lower case letters.

        :param unique_name: has to match unique_name exactly, i.e. capitalization matters
        :returns: taxid, scientific_name, unique_name, parent, rank or :raises: UniqueNameNotFoundError
        """
        self.db.execute(
            '''SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids WHERE UPPER(unique_name) IS ?''',
            (unique_name.upper(),))
        result = self.db.fetchone()
        if not result:
            raise UniqueNameNotFoundError('unique_name {} not found. Update the database?'.format(unique_name))
        else:
            taxid, scientific_name, unique_name, parent, rank = result
        return taxid, scientific_name, unique_name, parent, rank

    def get_taxid_values_by_name(self, name: str) -> (int, str, str, int, str):
        """
        Return taxids that corresponds to a specific unique_name. Returns list of results.
        Ignores upper/lower case letters.

        :param name: has to match unique_name exactly, i.e. capitalization matters
        :returns: taxid, scientific_name, unique_name, parent, rank or :raises: NameNotFoundError
        """
        self.db.execute(
            '''SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids WHERE UPPER(scientific_name) IS ?''',
            (name.upper(),))
        result = self.db.fetchone()
        if not result:
            raise NameNotFoundError('name {} not found. Update the database?'.format(name))
        else:
            taxid, scientific_name, name, parent, rank = result
        return taxid, scientific_name, name, parent, rank

    def get_taxid_values_by_id(self, taxid: int) -> (int, str, str, int, str):
        """:returns: taxid, scientific_name, unique_name, parent, rank or :raises: TaxIdNnotFoundError"""
        self.db.execute('''SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids WHERE taxid=?''',
                        (taxid,))
        result = self.db.fetchone()
        if not result:
            raise TaxIdNnotFoundError('TaxID {} not found. Update the database?'.format(taxid))
        taxid, scientific_name, unique_name, parent, rank = result

        return taxid, scientific_name, unique_name, parent, rank

    def get_scientific_name(self, taxid: int) -> str:
        """:returns: scientific name or :raises: TaxIdNnotFoundError"""

        taxid, scientific_name, unique_name, parent, rank = self.get_taxid_values_by_id(taxid)

        return scientific_name

    def get_unique_name(self, taxid: int) -> str:
        """:returns: unique name or :raises: TaxIdNnotFoundError"""

        taxid, scientific_name, unique_name, parent, rank = self.get_taxid_values_by_id(taxid)

        return unique_name

    def get_parent(self, taxid: int) -> int:
        """:returns: parent's TaxID or :raises: TaxIdNnotFoundError"""

        taxid, scientific_name, unique_name, parent, rank = self.get_taxid_values_by_id(taxid)

        return parent

    def get_rank(self, taxid: int) -> str:
        """:returns: rank or :raises: TaxIdNnotFoundError"""

        taxid, scientific_name, unique_name, parent, rank = self.get_taxid_values_by_id(taxid)

        return rank

    def query_taxid_unique_names(self, query, rank: str = None, size: int = 20, startswith=True) -> list:
        """
        Search for taxids by unique_name. Returns list of results.

        :param query: string to be searched
        :param rank: optional, taxonomic rank. example: 'species' or 'genus'
        :param size: number of results to be returned. default = 20, for all results, set to None
        :param startswith: if True: unique_names start with query; if False: unique_names contain query
        :returns: list of tuples: [(taxid, scientific_name, unique_name, parent, rank), ...]
        """
        query = f'{query}%' if startswith else f'%{query}%'

        if rank:
            self.db.execute('''
                SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids
                WHERE rank IS ? AND LIKE(?, unique_name)=TRUE
                ORDER BY taxid
            ''', (rank, query,))
        else:
            self.db.execute('''
                SELECT taxid, scientific_name, unique_name, parent, rank FROM taxids 
                WHERE LIKE(?, unique_name)=TRUE
                ORDER BY taxid
            ''', (query,))

        if size:
            taxids = self.db.fetchmany(size=size)
        else:
            taxids = self.db.fetchall()

        if not taxids:
            return []

        return taxids

    def update_ncbi_taxonomy_from_web(self):
        """
        Download taxdump.tar.gz from ftp.ncbi.nlm.nih.gov,
        then unpacks the relevant files to create a SQlite db.
        """
        import urllib.request
        import shutil
        import tarfile
        import tempfile

        if os.path.isfile(self.sqlite_db):
            os.remove(self.sqlite_db)

        # Download taxdump.tar.gz as temporary file
        f_taxdump = tempfile.TemporaryFile(suffix='.tar.gz', mode='w+b')
        print('Downloading taxdump.tar.gz from ftp.ncbi.nlm.nih.gov to temp...')
        with urllib.request.urlopen('ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz') as repsonse:
            shutil.copyfileobj(repsonse, f_taxdump)

        # Open taxdump.tar.gz as tarfile
        f_taxdump.flush()
        f_taxdump.seek(0)

        with tarfile.open(fileobj=f_taxdump) as f_tar:
            self.__load_ncbi_tar(f_tar)

        f_taxdump.close()

    def update_ncbi_taxonomy_from_file(self, taxdump_path):
        """
        Load local taxdump.tar.gz,
        then unpacks the relevant files to create a SQlite db.
        """
        assert os.path.isfile(taxdump_path)
        import tarfile

        if os.path.isfile(self.sqlite_db):
            os.remove(self.sqlite_db)

        with tarfile.open(taxdump_path) as f_tar:
            self.__load_ncbi_tar(f_tar)

    def __load_ncbi_tar(self, f_tar):
        """
        :param f_tar: taxdump.tar.gz as tarfile
        """
        taxid_to_names = self.__load_names_dmp(f_tar)
        self.__load_nodes_dmp(f_tar, taxid_to_names)

    def __load_names_dmp(self, f_tar):
        """
        Load names.dmp into dictionary

        :param f_tar: taxdump.tar.gz as tarfile
        """
        print(f'Loading names.dmp into {self.sqlite_db} ...')

        taxid_to_names = dict()  # taxid -> (scientific_name, unique_name)

        with f_tar.extractfile('names.dmp') as f_names:
            line = f_names.readline()
            while line:
                line = line.decode('utf-8').strip().split('\t')
                if line[6] == 'scientific name':
                    taxid = int(line[0])
                    scientific_name = line[2]
                    unique_name = scientific_name if line[4] == '' else line[4]

                    taxid_to_names[taxid] = (scientific_name, unique_name)

                line = f_names.readline()

        n_unique_sci_names = len(set(taxid_to_names.values()))
        n_taxids = len(taxid_to_names)
        assert n_unique_sci_names == n_taxids

        return taxid_to_names

    def __load_nodes_dmp(self, f_tar, taxid_to_names: dict):
        """
        Load nodes.dmp into SQlite

        :param f_tar: taxdump.tar.gz as tarfile
        """
        print(f'Loading nodes.dmp into {self.sqlite_db} ...')

        assert not os.path.isfile(self.sqlite_db)

        db = sqlite3.connect(self.sqlite_db, check_same_thread=False)
        try:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE taxids(
                    taxid INTEGER PRIMARY KEY,
                    scientific_name TEXT,
                    unique_name TEXT UNIQUE,
                    parent INTEGER,
                    rank TEXT
                )
            ''')
            db.commit()
            cursor = db.cursor()

            with f_tar.extractfile('nodes.dmp') as f_nodes:
                line = f_nodes.readline()
                while line:
                    line = line.decode('utf-8').strip().split('\t')

                    taxid = int(line[0])
                    parent = int(line[2])
                    rank = line[4]
                    scientific_name, unique_name = taxid_to_names[taxid]

                    cursor.execute('''
                        INSERT INTO taxids(taxid, scientific_name, unique_name, parent, rank)
                        VALUES(?,?,?,?,?)
                    ''', (taxid, scientific_name, unique_name, parent, rank))

                    line = f_nodes.readline()

            db.commit()

        except Exception as e:
            if os.path.isfile(self.sqlite_db):
                os.remove(self.sqlite_db)
            raise e
        finally:
            db.close()
