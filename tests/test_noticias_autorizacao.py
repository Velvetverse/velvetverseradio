#!/usr/bin/env python3
"""As APIs pagas permanecem bloqueadas sem autorização explícita, inclusive fora do Actions."""
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import velvetverse_noticias_producao as prod

old=os.environ.pop("VV_ALLOW_BILLABLE",None)
try:
    for fn in (prod.draft,prod.render):
        try:fn()
        except ValueError as error:
            assert "autorização explícita" in str(error),str(error)
        else:raise AssertionError(fn.__name__+" não bloqueou a API paga")
finally:
    if old is not None:os.environ["VV_ALLOW_BILLABLE"]=old
print("PASS: chamadas de redação e locução pagas bloqueadas sem consentimento.")
