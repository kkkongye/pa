"""User-side crypto helpers (deterministic stubs).

These mirror TP's stub helpers to keep tests deterministic.
Replace with real crypto (e.g., HKDF/HMAC, Paillier, etc.) in production.
"""
from typing import Any
import secrets
import hashlib
import json


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_r_bind() -> str:
    # Binding randomness (stub)
    return secrets.token_hex(16)


def compute_af(pii: dict, bi: dict, r_bind: str, pk_ap: str = "ap.pk.placeholder") -> str:
    """Compute AF from PII/BI/r_bind/pk_ap (deterministic stub).

    AF := sha256( canonical_json({pii,bi,r_bind,pk_ap}) )
    """
    payload = {"pii": pii, "bi": bi, "r_bind": r_bind, "pk_ap": pk_ap}
    return sha256_hex(canonical_json(payload))


def compute_cmi(pii: dict) -> str:
    """Compute CMI (Content Meta Index) as a hash of PII (stub)."""
    return sha256_hex(canonical_json(pii))


def sign_with_secret(secret: str, data: Any) -> str:
    # Deterministic signature stub to match TP
    return sha256_hex(secret + "|" + canonical_json(data))
