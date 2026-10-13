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
    lines=list(csv.DictReader(io.StringIO(text)))
    if len(lines)<5: raise ValueError("Ranking com menos de cinco registos")
    header={k.strip().lower():k for k in lines[0] if k is not None}
    print("CSV content type:",content_type,"rows:",len(lines),"headers:",list(lines[0].keys()))
    print("First CSV records:",repr(lines[:2])[:1800])
    rk=header.get("rank"); ak=header.get("artist") or header.get("subtitle")
    tk=header.get("title") or header.get("name")
    if not all((rk,ak,tk)): raise ValueError("Cabecalhos CSV inesperados: "+repr(list(lines[0])))
    first=lines[:5]
    if [int(r[rk]) for r in first] != [1,2,3,4,5]:
        raise ValueError("As cinco primeiras posicoes nao sao 1,2,3,4,5")
    matches=[]
    for row in first:
        title=(row.get(tk) or "").strip(); artist=(row.get(ak) or "").strip()
        if not title or not artist: raise ValueError("Musica sem titulo ou artista")
        query=urllib.parse.urlencode({"term": title+" "+artist,"entity":"song","country":"us","limit":50})
        body,_=get("https://itunes.apple.com/search?"+query)
        results=json.loads(body).get("results",[])
        valid=[item for item in results if normalized(item.get("trackName",""))==normalized(title)
               and normalized(artist).split(" ")[0] in normalized(item.get("artistName","")).split(" ")
               and str(item.get("trackId","")).isdigit()]
        if not valid:
            raise ValueError("Sem correspondencia Apple Music inequívoca: "+title+" / "+artist)
        matches.append({"rank":int(row[rk]),"title":title,"artist":artist,"apple_music_id":str(valid[0]["trackId"])})
    print(json.dumps({"source":URL,"content_type":content_type,"top5":matches},ensure_ascii=False,indent=2))
    print("SUCESSO: CSV atual lido e cinco IDs Apple Music encontrados. NENHUM ficheiro de producao modificado.")

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("TESTE FALHOU — producao intacta: "+str(e),file=sys.stderr)
        sys.exit(1)
