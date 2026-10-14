"""Shared adapter contract for the S&P 500 Corporate Stack, v0.2.0.

Every vendor on the shared shelf implements the same interface. Adapters run
in demo mode (fixture-backed, $0, no credentials) by default; live mode
activates when the required env keys are present. Keys are never committed.
"""

import abc
import base64
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request


class AdapterError(Exception):
    """A live vendor call failed. Never carries credential values."""


def http_json(method, url, headers=None, body=None, timeout=20,
              client_cert=None, client_key=None):
    """Minimal stdlib JSON HTTP client. Returns the decoded JSON body.

    client_cert/client_key enable mutual TLS (Visa Developer sandbox).
    Raises AdapterError on HTTP or network failure, without leaking secrets.
    """
    data = None
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=req_headers,
                                 method=method)
    ctx = None
    if client_cert:
        ctx = ssl.create_default_context()
        ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8")[:500]
        except Exception:
            detail = ""
        raise AdapterError("HTTP %s from %s: %s"
                           % (e.code, _host(url), detail))
    except Exception as e:
        raise AdapterError("request to %s failed: %s"
                           % (_host(url), type(e).__name__))


def http_form(method, url, fields, headers=None, timeout=20,
              basic_user=None, basic_pass=None):
    """Form-encoded POST helper (Twilio, OAuth token endpoints)."""
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if basic_user is not None:
        token = base64.b64encode(
            ("%s:%s" % (basic_user, basic_pass or "")).encode()).decode()
        req_headers["Authorization"] = "Basic " + token
    req = urllib.request.Request(url, data=data, headers=req_headers,
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw or "{}")
            except ValueError:
                return {"raw": raw[:500]}
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8")[:500]
        except Exception:
            detail = ""
        raise AdapterError("HTTP %s from %s: %s"
                           % (e.code, _host(url), detail))
    except Exception as e:
        raise AdapterError("request to %s failed: %s"
                           % (_host(url), type(e).__name__))


def _host(url):
    return urllib.parse.urlparse(url).netloc


class Adapter(abc.ABC):
    """One vendor's seat on the shared shelf.

    Subclasses set the class attributes and implement capabilities(),
    demo(), and live(). run() picks live when every env key is present,
    otherwise demo.
    """

    ticker = ""        # S&P 500 ticker, verified against data/constituents.csv
    vendor = ""        # company name
    category = ""      # primary capability category from data/categories.json
    product = ""       # the product used
    api_name = ""      # the developer API used
    docs_url = ""      # vendor API docs
    env_keys = ()      # env vars required for live mode

    @abc.abstractmethod
    def capabilities(self):
        """List of human-readable capability strings."""

    @abc.abstractmethod
    def demo(self):
        """Fixture-backed result. Always works, $0, no credentials."""

    @abc.abstractmethod
    def live(self):
        """One real endpoint call against the vendor's API."""

    def run(self):
        missing = [k for k in self.env_keys if not os.environ.get(k)]
        if missing:
            return {
                "mode": "demo",
                "ticker": self.ticker,
                "vendor": self.vendor,
                "category": self.category,
                "product": self.product,
                "result": self.demo(),
                "note": ("demo mode: set %s for a live call"
                         % ", ".join(self.env_keys)),
            }
        try:
            result = self.live()
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError("%s live call failed: %s"
                               % (self.vendor, type(e).__name__))
        return {
            "mode": "live",
            "ticker": self.ticker,
            "vendor": self.vendor,
            "category": self.category,
            "product": self.product,
            "result": result,
            "note": "live call against %s" % self.api_name,
        }

    def describe(self):
        return {
            "ticker": self.ticker,
            "vendor": self.vendor,
            "category": self.category,
            "product": self.product,
            "api": self.api_name,
            "docs": self.docs_url,
            "capabilities": self.capabilities(),
            "env_keys": list(self.env_keys),
            "live_ready": all(os.environ.get(k) for k in self.env_keys),
        }
