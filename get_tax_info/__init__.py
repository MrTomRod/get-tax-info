try:
    from importlib.metadata import version as _version
except ImportError:
    # For Python < 3.8
    from importlib_metadata import version as _version

try:
    __version__ = _version("get-tax-info")
except Exception:
    __version__ = "unknown"

from .tax_id import TaxID
from .get_tax_info import GetTaxInfo
from .get_busco import GetBusco
from .utils import TaxIdNnotFoundError, UniqueNameNotFoundError, NameNotFoundError, BuscoParentNotFoundError
