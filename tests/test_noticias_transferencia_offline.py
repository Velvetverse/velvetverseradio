#!/usr/bin/env python3
"""Ensaio offline do percurso MP3 -> manifesto R2 simulado -> staging no Windows.
Não faz chamadas de rede e não modifica o RadioDJ.
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import velvetverse_noticias_transferencia as tr

class FakeS3:
    def __init__(self):
        self.objects={}
    def upload_file(self,source,bucket,key,ExtraArgs=None):
        self.objects[(bucket,key)]=Path(source).read_bytes()
    def put_object(self,Bucket,Key,Body,ContentType=None):
        self.objects[(Bucket,Key)]=Body
    def get_object(self,Bucket,Key):
        return {"Body":io.BytesIO(self.objects[(Bucket,Key)])}
    def download_file(self,bucket,key,destination):
        Path(destination).write_bytes(self.objects[(bucket,key)])
    def head_object(self,Bucket,Key):
        return {"ContentLength":len(self.objects[(Bucket,Key)])}

def run(*args):
    old=sys.argv
    sys.argv=["transferencia.py",*args]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            tr.main()
    finally:
        sys.argv=old

def test():
    fake=FakeS3()
    sys.modules["boto3"]=types.SimpleNamespace(client=lambda *a,**k:fake)
    names=("R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET")
    prior={k:os.environ.get(k) for k in names}
    os.environ.update({"R2_ACCOUNT_ID":"0"*32,"R2_ACCESS_KEY_ID":"EXEMPLO",
                       "R2_SECRET_ACCESS_KEY":"EXEMPLO","R2_BUCKET":"bucket-simulado"})
    try:
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            audio=base/("velvetverse-noticias-"+tr.sunday()+"-ENSAIO.mp3")
            audio.write_bytes(b"ID3"+bytes(range(256))*10)
            run("upload","--file",str(audio))
            prefix="noticias/piloto/"+tr.sunday()
            manifest=json.loads(fake.objects[("bucket-simulado",prefix+"/manifest.json")])
            assert manifest["estado"]=="PRIVADO_STAGING_NAO_EMITIR"
            assert manifest["sha256"]==tr.hfile(audio)
            received=base/"Staging"
            run("receive","--destination",str(received))
            dest=received/("vv-noticias-"+tr.sunday()+"-STAGING.mp3")
            assert dest.read_bytes()==audio.read_bytes()
            run("receive","--destination",str(received))
            assert len(list(received.glob("*.mp3")))==1
            dest.write_bytes(b"alterado")
            try:
                run("receive","--destination",str(received))
            except RuntimeError:
                pass
            else:
                raise AssertionError("Receção aceitou substituição de MP3 alterado")
            assert not list(received.glob("*.download"))
    finally:
        for k,v in prior.items():
            if v is None:os.environ.pop(k,None)
            else:os.environ[k]=v
        sys.modules.pop("boto3",None)
    print("PASS: upload, manifesto, SHA256, download, repetição e bloqueio de ficheiro alterado.")
if __name__=="__main__":
    test()
