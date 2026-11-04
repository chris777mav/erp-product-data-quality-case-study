#!/usr/bin/env python3
"""Checks for the public, synthetic portfolio release (no V3 desktop claims)."""
from pathlib import Path
import sys,subprocess
R=Path(__file__).resolve().parents[1]
for item in ['tests/test_public_release.py','tests/test_dq_negativproben.py','tests/test_powerbi_source.py','tests/test_risk_integration.py']:
    print('==>',item,flush=True)
    subprocess.run([sys.executable,str(R/item)],cwd=R,check=True)
print('PUBLIC-RELEASE TESTS PASS (local/static only, no GitHub push or ERP/WMS live test)')
