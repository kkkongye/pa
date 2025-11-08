# Trust Provider (TP) skeleton

This folder contains a minimal Trust Provider (TP) skeleton service that
implements the basic endpoints described in the PA.md design. It is meant
to be a starting point and contains clearly-marked cryptographic stubs.

Files:

- `crypto.py`: Paillier and chameleon-hash stubs (replace with real libs).
- `phc.py`: PHC JSON-LD builder and simple verifier (stubbed signature).
- `service.py`: FastAPI APIRouter exposing `/tp/issue_phc`, `/tp/verify_phc`, `/tp/trace`.

How to use (developer):

1. Mount the router into the main FastAPI app in `octopus/octopus.py` or run
   a separate FastAPI instance that includes this router.

2. Replace the stubbed crypto implementations in `crypto.py` with real
   Paillier and chameleon-hash implementations, and add IPFS upload/lookup.

3. Implement real signing/verification for PHC.PROOF and secure key storage.
