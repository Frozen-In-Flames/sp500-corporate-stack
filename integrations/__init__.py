"""S&P 500 Corporate Stack integrations: the executable shared shelf."""

from .adapter import Adapter, AdapterError
from .adapters import ALL as ADAPTERS

__all__ = ["Adapter", "AdapterError", "ADAPTERS"]
