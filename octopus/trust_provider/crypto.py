"""Minimal crypto helpers for TP skeleton.

These are simple, clearly-marked stubs. Replace with proper crypto libs
for production (Paillier, chameleon hash, IPFS helpers).
Also contains deterministic signing helpers for basic consistency checks.
"""
from dataclasses import dataclass
from typing import Any, Dict
import json
import secrets
import hashlib


@dataclass
class PaillierKeypair:
    public: Dict[str, Any]
    private: Dict[str, Any]


def generate_paillier_keypair(nbits: int = 2048) -> PaillierKeypair:
    """Generate a fake Paillier keypair (stub).

    Produces deterministic-like placeholders. Replace with real implementation.
    """
    # WARNING: This is NOT real crypto. Use real Paillier lib in production.
    pub = {"n": secrets.token_hex(nbits // 8), "g": "g_placeholder"}
    priv = {"lambda": secrets.token_hex(nbits // 8), "mu": "mu_placeholder"}
    return PaillierKeypair(public=pub, private=priv)


def paillier_encrypt(pub: Dict[str, Any], plaintext: str) -> str:
    """Stub encrypt: JSON placeholder."""
    payload = {"p": plaintext}
    return json.dumps(payload, ensure_ascii=False)


def paillier_decrypt(priv: Dict[str, Any], ciphertext: str) -> str:
    """Stub decrypt to invert paillier_encrypt."""
    try:
        data = json.loads(ciphertext)
        return data.get("p", "")
    except Exception:
        return ""


def generate_chameleon_hash(message: str) -> Dict[str, str]:
    """Stub for chameleon-hash (returns hash and trapdoor stub)."""
    # Use randomness so each call differs; real CH should support trapdoor usage
    payload = f"{message}|{secrets.token_hex(8)}"
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {"hash": h, "trapdoor": secrets.token_hex(16)}


def canonical_json(obj: Any) -> str:
    """Return canonical JSON string for deterministic hashing/signing."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sign_with_secret(secret: str, data: Any) -> str:
    """Deterministic signature stub using secret + canonical_json(data)."""
    payload = canonical_json(data)
    return sha256_hex(secret + "|" + payload)


def verify_with_secret(secret: str, data: Any, signature: str) -> bool:
    return sign_with_secret(secret, data) == signature

