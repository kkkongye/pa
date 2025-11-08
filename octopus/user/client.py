"""HTTP client for interacting with TP endpoints remotely."""
from typing import Any, Dict
import httpx
from .crypto import compute_af, compute_cmi, compute_r_bind
from .models import UserInfo, PHCResponse


def request_phc_remote(base_url: str, user: UserInfo) -> PHCResponse:
    """Generate AF/CMI then POST to TP /v1/tp/issue_phc endpoint.

    Assumes TP router mounted under /v1/tp.
    Sends flat fields (af, cmi, cdid, ecid) which TP service will expand.
    """
    r_bind = compute_r_bind()
    af = compute_af(user.pii.model_dump(), user.bi.model_dump(), r_bind)
    cmi = compute_cmi(user.pii.model_dump())

    payload = {
        "af": af,
        "cmi": cmi,
        "cdid": user.cdid,
        "ecid": user.ecid,
    }
    url = base_url.rstrip("/") + "/v1/tp/issue_phc"
    resp = httpx.post(url, json=payload, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    return PHCResponse(**data)
