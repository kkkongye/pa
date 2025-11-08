"""Full-flow tests for the Trust Provider skeleton.

This script constructs a PHC consistent with the PA.md image (ASO with TPM
and APM, TPA and APA, and PROOF placeholders), then exercises the TP
endpoints implemented in `octopus.trust_provider.service`:

- issue_phc (via builder and via endpoint)
- verify_phc
- trace (using Paillier stub)

Run with the project's virtualenv active:

    python test_scripts/test_tp_full_flow.py

Note: these call the router functions directly (not HTTP). They use the
stubbed crypto implementations in `octopus.trust_provider.crypto`.
"""
from datetime import datetime
import json
import os
import sys

# Ensure project root is on sys.path when running as a script
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from octopus.trust_provider import service as tp_service
from octopus.trust_provider import phc as phc_module
from octopus.trust_provider import crypto as crypto_module


def build_sample_phc():
    """Build PHC matching the image structure: ASO with TPM/APM, TPA, APA, PROOF."""
    # ASO - TPM (TP metadata) and APM (AP metadata)
    aso = {
        "TPM": {
            "Time": datetime.utcnow().isoformat() + "Z",
            "CDID": "cdid:example:1234",
            "AF": "af_example_anchor",
            "ECID": "g",
        },
        "APM": {
            "Time": datetime.utcnow().isoformat() + "Z",
            "CMI": "cmi_hash_example",
        },
    }

    # TPA: use deterministic fields by calling service signing for test validity
    tpid = "tp.example"
    tp_secret = tp_service.TP_PAILLIER.private["lambda"]
    tpproof = crypto_module.sign_with_secret(tp_secret, {"TPM": aso["TPM"], "TPid": tpid})
    tpa = {"TPid": tpid, "TPproof": tpproof}

    # APA: AP proof placeholder
    apid = "ap.placeholder"
    ap_secret = "ap_secret_placeholder"
    approof = crypto_module.sign_with_secret(ap_secret, {"APM": aso["APM"], "APid": apid})
    apa = {"APid": apid, "APproof": approof}

    phc = phc_module.build_phc(aso=aso, tpa=tpa, apa=apa, tp_secret=tp_secret)
    return phc


def test_issue_verify_trace():
    print("Building sample PHC...")
    phc = build_sample_phc()
    print("PHC built:\n", json.dumps(phc, indent=2, ensure_ascii=False))

    print("Verifying PHC structure via TP verify endpoint...")
    # call verify endpoint function directly (it expects object with .phc attr)
    verify_req = type("Req", (), {"phc": phc})()
    res_verify = tp_service.verify_phc_endpoint(verify_req)
    assert res_verify.get("verified") is True
    print("PHC verification passed")

    print("Testing TP.issue_phc endpoint (issue with ASO-like input)...")
    # The issue_phc endpoint now accepts nested ASO (TPM/APM) or flat af/cmi inputs
    # For direct call (non-HTTP), pass Pydantic models so .model_dump() is available
    TPMModel = tp_service.TPMModel
    APMModel = tp_service.APMModel
    ASOCompleteModel = tp_service.ASOCompleteModel

    aso_input = ASOCompleteModel(
        TPM=TPMModel(Time=None, CDID="cdid:example:1234", AF="af_example_anchor", ECID="g"),
        APM=APMModel(Time=None, CMI="cmi_hash_example"),
    )
    res_issue = tp_service.issue_phc(aso_input)
    assert res_issue.get("success") is True
    issued_phc = res_issue.get("phc")
    print("Issued PHC id:", issued_phc.get("id"))

    print("Testing trace (encrypt sample ID and call trace endpoint)...")
    sample_real_id = "user_real_id_0001"
    # Encrypt with TP public key stub
    ciphertext = crypto_module.paillier_encrypt(tp_service.TP_PAILLIER.public, sample_real_id)
    trace_req = type("T", (), {"rf_ciphertext": ciphertext})()
    res_trace = tp_service.trace_identity(trace_req)
    assert res_trace.get("decrypted") == sample_real_id
    print("Trace decrypted value matches sample real id")

    print("All TP skeleton tests passed")


if __name__ == "__main__":
    test_issue_verify_trace()
