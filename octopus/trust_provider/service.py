"""Minimal FastAPI router exposing TP endpoints.

Endpoints implemented:
- POST /tp/issue_phc -> issue PHC with given ASO payload (returns PHC JSON-LD)
- POST /tp/verify_phc -> verify a PHC structure
- POST /tp/trace -> trace identity using RF ciphertext (stub decrypt)

The router is designed to be mountable into the main FastAPI app (octopus).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from .phc import build_phc, verify_phc, phc_to_json
from .crypto import (
    generate_paillier_keypair,
    paillier_decrypt,
    paillier_encrypt,
    generate_chameleon_hash,
    sign_with_secret,
)

router = APIRouter()


class TPMModel(BaseModel):
    Time: Optional[str] = None
    CDID: Optional[str] = None
    AF: str
    ECID: Optional[str] = None


class APMModel(BaseModel):
    Time: Optional[str] = None
    CMI: str


class ASOCompleteModel(BaseModel):
    TPM: Optional[TPMModel] = None
    APM: Optional[APMModel] = None

    # Fallback simplified inputs to auto-build TPM/APM if not provided
    af: Optional[str] = None
    cdid: Optional[str] = None
    ecid: Optional[str] = None
    cmi: Optional[str] = None


class PHCModel(BaseModel):
    phc: Dict[str, Any]


class TraceRequest(BaseModel):
    rf_ciphertext: str


# Create a simple in-memory keypair for TP (demo only)
TP_PAILLIER = generate_paillier_keypair()


@router.post("/tp/issue_phc")
def issue_phc(aso: ASOCompleteModel) -> Dict[str, Any]:
    """Issue a PHC for the provided ASO (Agent Self-Owned) payload.

    This endpoint will:
    - Construct ASO.TPM/APM (if missing) with required fields
    - Create TPA {TPid, TPproof} and APA {APid, APproof} placeholders
    - Compute PROOF {TPCH, APCH, CHproof, VM}
    - Return constructed PHC JSON-LD
    """
    from datetime import datetime

    # 1) Build ASO (TPM/APM)
    if aso.TPM and aso.APM:
        # Use provided structures; fill missing Time
        tpm = aso.TPM.model_dump()
        apm = aso.APM.model_dump()
        tpm.setdefault("Time", datetime.utcnow().isoformat() + "Z")
        apm.setdefault("Time", datetime.utcnow().isoformat() + "Z")
    else:
        # Fallback: build from flat fields
        if not aso.af or not aso.cmi:
            raise HTTPException(status_code=400, detail="Missing 'af' or 'cmi' for ASO when TPM/APM not provided")
        tpm = {
            "Time": datetime.utcnow().isoformat() + "Z",
            "CDID": aso.cdid or "cdid:placeholder",
            "AF": aso.af,
            "ECID": aso.ecid or "g",
        }
        apm = {
            "Time": datetime.utcnow().isoformat() + "Z",
            "CMI": aso.cmi,
        }

    aso_built = {"TPM": tpm, "APM": apm}

    # 2) TPA: choose TPid (use a deterministic id derived from public key stub)
    tpid = "tp.example"
    tpproof = sign_with_secret(TP_PAILLIER.private["lambda"], {"TPM": tpm, "TPid": tpid})
    tpa = {"TPid": tpid, "TPproof": tpproof}

    # 3) APA (placeholder): APproof is a stub signature with a fixed secret
    apid = "ap.placeholder"
    ap_secret = "ap_secret_placeholder"
    approof = sign_with_secret(ap_secret, {"APM": apm, "APid": apid})
    apa = {"APid": apid, "APproof": approof}

    # 4) Build PHC with PROOF fields
    phc = build_phc(aso=aso_built, tpa=tpa, apa=apa, tp_secret=TP_PAILLIER.private["lambda"])

    return {"success": True, "phc": phc}


@router.post("/tp/verify_phc")
def verify_phc_endpoint(payload: PHCModel) -> Dict[str, Any]:
    phc = payload.phc
    ok = verify_phc(phc, tp_secret=TP_PAILLIER.private["lambda"])  # enable deterministic checks
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid PHC structure or missing proof")
    return {"success": True, "verified": True}


@router.post("/tp/trace")
def trace_identity(req: TraceRequest) -> Dict[str, Any]:
    """Trace identity by decrypting RF (stub using paillier_decrypt).

    In production TP would use its Paillier private key to decrypt RF and
    fetch IPFS content for evidence. Here we just return the decrypted payload.
    """
    decrypted = paillier_decrypt(TP_PAILLIER.private, req.rf_ciphertext)
    return {"success": True, "decrypted": decrypted}
