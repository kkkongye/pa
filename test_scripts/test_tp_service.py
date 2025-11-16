"""Smoke tests for TP skeleton issue/verify logic.

This test avoids network calls and directly exercises the Pydantic models
expected by `issue_phc` and `verify_phc_endpoint`.
"""
import sys
from pathlib import Path

# Ensure project root on path when run directly
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from octopus.trust_provider.service import (
    issue_phc,
    verify_phc_endpoint,
    ASOCompleteModel,
    PHCModel,
)


def test_issue_and_verify():
    # Use the proper Pydantic model instead of a dynamic type to satisfy
    # attribute access for TPM/APM fallback construction inside issue_phc.
    aso = ASOCompleteModel(
        af="af_example",
        cmi="cmi_example",
        cdid="cdid_example",
        ecid="g",
    )
    res = issue_phc(aso)
    assert res["success"] is True, "issue_phc should return success"
    phc = res["phc"]
    # Wrap in PHCModel for verification endpoint
    verify_res = verify_phc_endpoint(PHCModel(phc=phc))
    assert verify_res["verified"] is True, "PHC should verify"
    # Basic structural sanity checks
    assert phc["ASO"]["TPM"]["AF"] == "af_example"
    assert "PROOF" in phc and phc["PROOF"].get("TPCH"), "PHC should contain PROOF.TPCH"
    print("TP skeleton issue/verify smoke test passed")


if __name__ == "__main__":
    test_issue_and_verify()
