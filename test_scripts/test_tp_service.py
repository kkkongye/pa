"""Quick smoke tests for the TP skeleton (import-only).

Run this script to ensure the TP router module can be imported and basic
builders run without error. It's not a network test.
"""
from octopus.trust_provider import service


def test_issue_and_verify():
    aso = type("A", (), {"af": "af_example", "cdid": "cdid_example", "metadata": {}})()
    res = service.issue_phc(aso)
    assert res["success"] is True
    phc = res["phc"]
    v = service.verify_phc_endpoint(type("P", (), {"phc": phc})())
    assert v["verified"] is True
    print("TP skeleton issue/verify smoke test passed")


if __name__ == "__main__":
    test_issue_and_verify()
