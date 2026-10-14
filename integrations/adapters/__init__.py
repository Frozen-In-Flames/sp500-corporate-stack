"""Vendor adapters. Every class here satisfies the shared Adapter contract."""

from .msft import MicrosoftAdapter
from .crm import SalesforceAdapter
from .twlo import TwilioAdapter
from .intu import QuickBooksAdapter
from .adbe import AdobeAdapter
from .amzn import AwsAdapter
from .googl import GoogleAdapter
from .visa import VisaAdapter
from .fdx import FedExAdapter
from .ups import UpsAdapter
from .csco import WebexAdapter
from .pypl import PayPalAdapter

ALL = [
    MicrosoftAdapter,
    SalesforceAdapter,
    TwilioAdapter,
    QuickBooksAdapter,
    AdobeAdapter,
    AwsAdapter,
    GoogleAdapter,
    VisaAdapter,
    FedExAdapter,
    UpsAdapter,
    WebexAdapter,
    PayPalAdapter,
]

__all__ = ["ALL"]
