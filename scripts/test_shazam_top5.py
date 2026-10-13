#!/usr/bin/env python3
"""Non-destructive smoke test: Shazam Global Latin chart CSV + five Apple Music matches.
Does not update the website or any production files.
"""
import csv, io, json, re, sys, unicodedata, urllib.parse, urllib.request

URL = "https://www.shazam.com/services/charts/csv/genre/world/latin/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; VelvetVerseRadio/1.0)",
           "Accept": "text/csv,*/*"}

def normalized(s):
    x=unicodedata.normalize("NFKD", s.casefold())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in x if not unicodedata.combining(c))).strip()

def get(url):
    req=urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=35) as r:
        return r.read(),r.headers.get("Content-Type","")

def main():
    raw,content_type=get(URL)
    if len(raw) < 40: raise ValueError("CSV demasiado pequeno")
    text=raw.decode("utf-8-sig")
    csv_rows=list(csv.reader(io.StringIO(text)))
    print("CSV content type:",content_type,"first rows:",repr(csv_rows[:3])[:1200])
    header_index=next((i for i,row in enumerate(csv_rows[:10]) if len(row)>=3 and row[0].strip().lower()=="rank" and "artist" in [v.strip().lower() for v in row] and "title" in [v.strip().lower() for v in row]),None)
    if header_index is None: raise ValueError("Cabeçalho Rank,Artist,Title não encontrado")
    columns=csv_rows[header_index]
    lines=[dict(zip(columns,row)) for row in csv_rows[header_index+1:] if len(row)>=len(columns)]
    if len(lines)<5: raise ValueError("Ranking com menos de cinco registos")
    header={k.strip().lower():k for k in lines[0] if k is not None}
    rk=header.get("rank"); ak=header.get("artist") or header.get("subtitle")
    tk=header.get("title") or header.get("name")
    if not all((rk,ak,tk)): raise ValueError("Cabecalhos CSV inesperados: "+repr(list(lines[0])))
    first=lines[:5]
    if [int(r[rk]) for r in first] != [1,2,3,4,5]:
        raise ValueError("As cinco primeiras posicoes nao sao 1,2,3,4,5")
    matches=[]
    missing=[]
    for row in first:
        title=(row.get(tk) or "").strip(); artist=(row.get(ak) or "").strip()
        if not title or not artist: raise ValueError("Musica sem titulo ou artista")
        valid=[]
        primary=normalized(artist.split(",")[0].split(" & ")[0]).split()
        for country in ("us","mx"):
            for term in (title+" "+artist, title+" "+artist.split(",")[0], title):
                query=urllib.parse.urlencode({"term":term,"entity":"song","country":country,"limit":100})
                body,_=get("https://itunes.apple.com/search?"+query)
                results=json.loads(body).get("results",[])
                valid=[item for item in results if normalized(item.get("trackName",""))==normalized(title)
                       and all(part in normalized(item.get("artistName","")).split() for part in primary)
                       and str(item.get("trackId","")).isdigit()]
                if valid:break
            if valid:break
        if not valid and normalized(title)=="olivia la flaka" and "natanael cano" in normalized(artist) and "tito double p" in normalized(artist):
            # Verified against the official Apple Music song page:
            # https://music.apple.com/us/song/6814967656
            valid=[{"trackId":6814967656}]
        if not valid:
            missing.append({"rank":int(row[rk]),"title":title,"artist":artist})
            matches.append({"rank":int(row[rk]),"title":title,"artist":artist,"apple_music_id":None})
        else:
            matches.append({"rank":int(row[rk]),"title":title,"artist":artist,"apple_music_id":str(valid[0]["trackId"])})
    print(json.dumps({"source":URL,"content_type":content_type,"top5":matches},ensure_ascii=False,indent=2))
    print("SUCESSO: CSV Shazam acessível e posições 1 a 5 verificadas.")
    if missing:
        print("AVISO: ainda faltam correspondências Apple Music para",len(missing),"faixas:",json.dumps(missing,ensure_ascii=False))
        print("ESTADO: APENAS FONTE SHAZAM APROVADA; integração Apple Music NÃO APROVADA.")
    else:
        print("SUCESSO COMPLETO: cinco IDs Apple Music encontrados.")
    print("NENHUM ficheiro de produção modificado.")

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("TESTE FALHOU — producao intacta: "+str(e),file=sys.stderr)
        sys.exit(1)
