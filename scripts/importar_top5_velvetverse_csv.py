#!/usr/bin/env python3
"""Importar ranking semanal de CSV RCast para um RASCUNHO JSON.
Nao publica site, nao altera votos, nao carrega audio. Falha em vez de adivinhar colunas.
Uso: python scripts/importar_top5_velvetverse_csv.py reporte.csv --out top5-velvetverse-candidato.json
"""
import argparse,csv,datetime as dt,json,re,sys,unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

ALIASES={
 "title":{"title","track","song","song title","track title","musica","titulo","título","faixa"},
 "artist":{"artist","artist name","artista","performer","interprete","intérprete"},
 "plays":{"plays","play count","playbacks","times played","reproducoes","reproduções","vezes tocada","count","total plays"},
 "listeners":{"listeners","audience","ouvintes","listener count","average listeners"},
}
def norm(v):
 v=unicodedata.normalize("NFKD",str(v or "")).encode("ascii","ignore").decode("ascii")
 return re.sub(r"\s+"," ",v.lower().strip()).strip()
def find_col(headers,key):
 found=[h for h in headers if norm(h) in {norm(x) for x in ALIASES[key]}]
 if len(found)!=1:raise ValueError("Coluna "+key+" ambigua/ausente; encontrados: "+repr(found))
 return found[0]
def number(v):
 s=str(v).strip().replace(" ","")
 if not re.fullmatch(r"\d{1,12}",s):raise ValueError("Numero de reproducoes invalido: "+repr(v))
 return int(s)
def import_csv(source,week):
 with source.open("r",encoding="utf-8-sig",newline="") as stream:
  head=stream.read(4096);stream.seek(0)
  dialect=csv.Sniffer().sniff(head,delimiters=",;\t")
  table=csv.DictReader(stream,dialect=dialect)
  headers=table.fieldnames or []
  names={key:find_col(headers,key) for key in ("title","artist","plays")}
  names["listeners"]=next((h for h in headers if norm(h) in {norm(x) for x in ALIASES["listeners"]}),None)
  combined={}
  for line,row in enumerate(table,2):
   artist=(row.get(names["artist"]) or "").strip()
   title=(row.get(names["title"]) or "").strip()
   if not artist or not title:continue
   plays=number(row.get(names["plays"]) or "0")
   if plays<1:continue
   if norm(title) in {"unknown","unknown title","station id","jingle","sweeper","advert","advertisement"}:continue
   key=(norm(artist),norm(title))
   if key not in combined:combined[key]={"artist":artist,"title":title,"plays":0}
   combined[key]["plays"]+=plays
 ranked=sorted(combined.values(),key=lambda x:(-x["plays"],norm(x["artist"]),norm(x["title"])))
 if len(ranked)<5:raise ValueError("Menos de cinco musicas validas no CSV")
 # Nao inventar desempate: a fonte pode apresentar varias musicas com a mesma contagem.
 if ranked[4]["plays"]==ranked[5]["plays"] if len(ranked)>5 else False:
  raise ValueError("Empate no quinto lugar: classificacao exige desempate editorial")
 if len({(s["artist"],s["title"]) for s in ranked[:5]})<5:raise ValueError("Duplicados no ranking")
 tracks=[]
 for i,s in enumerate(ranked[:5],1):
  tracks.append({"rank":i,"id":"vv-"+week+"-"+str(i),"title":s["title"],"artist":s["artist"],"playbacks":s["plays"],"artwork":"","preview":""})
 return {"edition":"velvetverse-"+week,"week":week,"source":"RCast — CSV importado; confirmar periodo e metrica de reproducoes","status":"provisional","voting_enabled":False,"preview_permission_confirmed":False,"previews_seconds":30,"songs":tracks}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("csv",type=Path)
 p.add_argument("--out",type=Path,default=Path("top5-velvetverse-candidato.json"))
 p.add_argument("--week",default=None,help="segunda-feira YYYY-MM-DD; por defeito a segunda corrente de Toronto")
 args=p.parse_args()
 now=dt.datetime.now(ZoneInfo("America/Toronto")).date()
 monday=now-dt.timedelta(days=now.weekday())
 week=args.week or monday.isoformat()
 day=dt.date.fromisoformat(week)
 if day.weekday()!=0:raise ValueError("A semana tem de comecar segunda-feira")
 if args.out.resolve()==Path("top5-velvetverse-weekly.json").resolve():
  raise ValueError("Nao alterar diretamente a edicao publicada")
 data=import_csv(args.csv,week)
 args.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("RASCUNHO criado em",args.out)
 for s in data["songs"]:print(f'#{s["rank"]} {s["artist"]} - {s["title"]}: {s["playbacks"]} reproducoes')
 print("Nao publicou ficheiros, nao enviou audios e nao reiniciou votos.")
if __name__=="__main__":
 try:main()
 except Exception as exc:print("IMPORTACAO BLOQUEADA:",exc,file=sys.stderr);sys.exit(2)
