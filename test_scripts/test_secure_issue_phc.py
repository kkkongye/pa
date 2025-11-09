"""End-to-end test for secure issuance flow.

This test mounts the TP router, fetches public keys, constructs an encrypted
request with a user signature (Ed25519) and ensures the PHC is issued.

Usage:
    pytest test_scripts/test_secure_issue_phc.py -vv
    python test_scripts/test_secure_issue_phc.py  # prints PASS line if ok
"""
import base64
import secrets
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from octopus.trust_provider.service import router
from octopus.user import crypto


app = FastAPI()
app.include_router(router, prefix="/v1")


def test_secure_issue_phc():
    client = TestClient(app)

    # 1) Fetch TP public keys
    keys = client.get("/v1/tp/public_keys").json()
    tp_pk_pem = keys["tp_encrypt_pk"]

    # 2) Generate user keys and r_bind
    sk, pk = crypto.generate_user_ed25519()
    r_bind = secrets.token_bytes(32)
    sig = crypto.sign_r_bind(sk, r_bind)

    # 3) Build plaintext
    af_hex = crypto.compute_af(
        {"name": "Alice", "id_number": "ID123", "email": "a@example.com"},
        {"login_count": 5, "reputation_score": 10.5, "last_login_ip": "127.0.0.1"},
        r_bind.hex(),
    )
    # Compact AF to base64 of raw digest to avoid RSA-OAEP size limits
    af_b64 = base64.b64encode(bytes.fromhex(af_hex)).decode()

    plaintext = {
        "AF": af_b64,
    # omit CMI to reduce payload size; server will fill placeholder
    "CDID": "cdid:test",
    "ECID": "g",
        "r_bind_b64": base64.b64encode(r_bind).decode(),
        "timestamp": int(time.time()),
    }

    # 4) Encrypt
    cr_b64 = crypto.encrypt_issue_plaintext(tp_pk_pem, plaintext)

    # 5) Send secure request
    payload = {
        "cr": cr_b64,
        "user_pub": base64.b64encode(pk).decode(),
        "sig": base64.b64encode(sig).decode(),
    }
    resp = client.post("/v1/tp/issue_phc_secure", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    phc = data["phc"]
    # Server stores AF in hex; plaintext AF was base64 of 32-byte digest
    expected_af_hex = base64.b64decode(plaintext["AF"]).hex()
    assert phc["ASO"]["TPM"]["AF"] == expected_af_hex


if __name__ == "__main__":
    test_secure_issue_phc()
    print("[secure-issue] PASS: Encrypted PHC issuance validated")
