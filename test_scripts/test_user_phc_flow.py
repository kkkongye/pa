"""Test user module PHC flow (local issue without HTTP server).

Ensures:
- AF and CMI deterministic for same inputs (with fixed r_bind override)
- Issued PHC contains matching AF in ASO.TPM
"""
import sys
from pathlib import Path

# Ensure project root on path when run directly
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from octopus.user.models import PIIModel, BIModel, UserInfo
from octopus.user.crypto import compute_af, compute_cmi
from octopus.user.flow import local_issue


def test_af_cmi_deterministic():
    pii = {"name": "Alice", "id_number": "ID123", "email": "a@example.com"}
    bi = {"login_count": 5, "reputation_score": 10.5, "last_login_ip": "127.0.0.1"}
    r_bind = "fixed_r_bind"  # Force determinism
    af1 = compute_af(pii, bi, r_bind)
    af2 = compute_af(pii, bi, r_bind)
    assert af1 == af2, "AF should be deterministic for same inputs"
    cmi1 = compute_cmi(pii)
    cmi2 = compute_cmi(pii)
    assert cmi1 == cmi2, "CMI should be deterministic"


def test_local_issue_flow():
    user = UserInfo(
        pii=PIIModel(name="Alice", id_number="ID123", email="a@example.com"),
        bi=BIModel(login_count=5, reputation_score=10.5, last_login_ip="127.0.0.1"),
    )
    result = local_issue(user)
    phc = result["phc_response"]["phc"]
    af_built = result["af_result"]["af"]
    # Check AF inside PHC
    assert phc["ASO"]["TPM"]["AF"] == af_built, "PHC AF must match computed AF"
    assert phc["PROOF"].get("TPCH"), "PHC should include TPCH"


if __name__ == "__main__":
    # Simple manual run output
    test_af_cmi_deterministic()
    test_local_issue_flow()
    print("User PHC flow tests passed")
