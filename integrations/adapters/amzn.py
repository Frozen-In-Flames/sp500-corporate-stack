"""Amazon (AMZN) adapter: AWS via SigV4-signed STS, stdlib only."""

import datetime
import hashlib
import hmac
import os
import urllib.parse

from ..adapter import Adapter, http_json


def _sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _sigv4_headers(access_key, secret_key, region, service,
                   method, url, params):
    """Build AWS Signature Version 4 headers for a query-string request."""
    now = datetime.datetime.now(datetime.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    canonical_qs = "&".join(
        "%s=%s" % (k, urllib.parse.quote(str(v), safe="~"))
        for k, v in sorted(params.items()))
    canonical_headers = ("host:%s\nx-amz-date:%s\n" % (host, amzdate))
    signed_headers = "host;x-amz-date"
    payload_hash = hashlib.sha256(b"").hexdigest()
    canonical = "\n".join([method, parsed.path or "/", canonical_qs,
                           canonical_headers, signed_headers, payload_hash])
    scope = "%s/%s/%s/aws4_request" % (datestamp, region, service)
    string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amzdate, scope,
                                hashlib.sha256(
                                    canonical.encode()).hexdigest()])
    k = _sign(("AWS4" + secret_key).encode(), datestamp)
    k = _sign(k, region)
    k = _sign(k, service)
    k = _sign(k, "aws4_request")
    signature = hmac.new(k, string_to_sign.encode(),
                         hashlib.sha256).hexdigest()
    auth = ("AWS4-HMAC-SHA256 Credential=%s/%s, SignedHeaders=%s, "
            "Signature=%s" % (access_key, scope, signed_headers, signature))
    return {"x-amz-date": amzdate, "Authorization": auth}


class AwsAdapter(Adapter):
    ticker = "AMZN"
    vendor = "Amazon"
    category = "compute"
    product = "AWS"
    api_name = "AWS STS GetCallerIdentity (SigV4)"
    docs_url = "https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html"
    env_keys = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")

    def capabilities(self):
        return ["identity verification via STS",
                "S3, EC2 and the full AWS API family (same signing)"]

    def demo(self):
        return {"action": "sts_get_caller_identity",
                "identity": {"UserId": "demo-AIDACKCEVSQ6C2EXAMPLE",
                             "Account": "123456789012",
                             "Arn": "arn:aws:iam::123456789012:user/demo"},
                "fixture": True}

    def live(self):
        key = os.environ["AWS_ACCESS_KEY_ID"]
        secret = os.environ["AWS_SECRET_ACCESS_KEY"]
        url = "https://sts.amazonaws.com/"
        params = {"Action": "GetCallerIdentity", "Version": "2011-06-15"}
        headers = _sigv4_headers(key, secret, "us-east-1", "sts",
                                 "POST", url, params)
        headers["Content-Type"] = ("application/x-www-form-urlencoded; "
                                   "charset=utf-8")
        full = url + "?" + urllib.parse.urlencode(params)
        import urllib.request
        req = urllib.request.Request(full, data=b"", headers=headers,
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as e:
            from ..adapter import AdapterError
            raise AdapterError("AWS STS request failed: %s"
                               % type(e).__name__)
        import re
        def tag(name):
            m = re.search("<%s>(.*?)</%s>" % (name, name), raw, re.S)
            return m.group(1).strip() if m else None
        return {"action": "sts_get_caller_identity",
                "userId": tag("UserId"), "account": tag("Account"),
                "arn": tag("Arn")}
