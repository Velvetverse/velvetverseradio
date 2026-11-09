#!/usr/bin/env python3
"""Calcula Top 5 por diferenca de dois instantaneos CSV do MESMO MES RCast.
So le CSV e escreve rascunho JSON. Nao publica audio, nao altera site ou votos.
"""
import argparse,datetime as dt,json,sys
from pathlib import Path
import importar_top5_velvetverse_csv as parser

def counts(path):
 with path.open("r",encoding="utf-8-sig",newline="") as f:
  import csv
  prefix=f.read(4096);f.seek(0)
  dialect=csv.Sniffer().sniff(prefix,delimiters=",;\t")
  rows=csv.DictReader(f,dialect=dialect)
  fields=rows.fieldnames or []
  title=parser.find_col(fields,"title")
  artist=parser.find_col(fields,"artist")
  plays=parser.find_col(fields,"plays")
  data={}
  for row in rows:
   t=parser.clean_title((row.get(title) or "").strip())
   a=(row.get(artist) or "").strip()
   if not t or not a or parser.is_technical(t,a):continue
   n=parser.number(row.get(plays) or "0")
   key=(parser.norm(a),parser.norm(t))
   if key not in data:data[key]={"artist":a,"title":t,"plays":0}
   data[key]["plays"]+=n
  return data

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("anterior",type=Path)
 ap.add_argument("atual",type=Path)
 ap.add_argument("--anterior-data",required=True,help="AAAA-MM-DD do instantaneo anterior")
 ap.add_argument("--atual-data",required=True,help="AAAA-MM-DD do instantaneo atual")
 ap.add_argument("--out",type=Path,default=Path("top5-velvetverse-semanal-candidato.json"))
 args=ap.parse_args()
 before=dt.date.fromisoformat(args.anterior_data)
 after=dt.date.fromisoformat(args.atual_data)
 if after<=before or (after-before).days>8:raise ValueError("Datas devem delimitar um intervalo de ate oito dias")
 if before.year!=after.year or before.month!=after.month:
  raise ValueError("Transicao de mes exige dois pares de instantaneos, um por mes; nao subtrair meses diferentes")
 start=counts(args.anterior);end=counts(args.atual)
 all_keys=set(start)|set(end)
 changes=[]
 for key in all_keys:
  previous=start.get(key,{"plays":0})["plays"]
  current=end.get(key,{"plays":0})["plays"]
  if current<previous:raise ValueError("Contagem diminuiu para %s - verificar se houve reset ou correcao no RCast"%(key,))
  delta=current-previous
  if delta:
   info=end[key]
   changes.append({"title":info["title"],"artist":info["artist"],"plays":delta})
 changes.sort(key=lambda x:(-x["plays"],parser.norm(x["artist"]),parser.norm(x["title"])))
 if len(changes)<5:raise ValueError("Menos de cinco musicas no intervalo")
 if len(changes)>5 and changes[4]["plays"]==changes[5]["plays"]:
  raise ValueError("Empate no quinto lugar: nao inventar desempate")
 week=after.isoformat()
 songs=[{"rank":i,"id":"vv-"+week+"-"+str(i),"title":s["title"],"artist":s["artist"],
         "playbacks":s["plays"],"artwork":"","preview":""} for i,s in enumerate(changes[:5],1)]
 data={"edition":"velvetverse-"+week,"week":week,
       "source":"RCast — diferenca entre instantaneos mensais de "+before.isoformat()+" e "+after.isoformat(),
       "status":"provisional","voting_enabled":False,"preview_permission_confirmed":False,
       "previews_seconds":30,"songs":songs}
 if args.out.name=="top5-velvetverse-weekly.json":raise ValueError("Nao sobrescrever edicao do site")
 args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 for s in songs:print("#%s %s — %s: +%s"%(s["rank"],s["artist"],s["title"],s["playbacks"]))
 print("RASCUNHO:",args.out,"- nenhum ficheiro publicado.")
if __name__=="__main__":
 try:main()
 except Exception as e:print("BLOQUEADO:",e,file=sys.stderr);sys.exit(2)
