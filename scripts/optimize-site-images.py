#!/usr/bin/env python3
"""Create optimized WebP copies and safely update local image references.
Original images stay in the repository. Run from repository root.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import quote
import html, json, re, subprocess
from PIL import Image, ImageOps

ROOT=Path.cwd()
files=[Path(x) for x in subprocess.check_output(["git","ls-files","-z"]).decode("utf-8").split("\0") if x]
images=[p for p in files if p.suffix.lower() in (".png",".jpg",".jpeg") and p.is_file()]
# Keep install/manifest icons, QR codes, and other small utility assets unchanged.
def skip_image(p):
    n=p.name.lower()
    return n in {"icon-192.png","icon-512.png","apple-touch-icon.png","favicon.png","favicon.jpg","favicon.ico","android.png","iphone.png"} or "qr" in n or n.startswith("icon-") or p.stat().st_size < 30000

mapping={}
stats=[]
for p in images:
    if skip_image(p): continue
    try:
        with Image.open(p) as original:
            if getattr(original,"n_frames",1)>1: continue
            im=ImageOps.exif_transpose(original)
            im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
            if im.mode not in ("RGB","RGBA"): im=im.convert("RGBA" if "transparency" in im.info else "RGB")
            target=p.with_name(p.name+".webp")
            im.save(target,"WEBP",quality=85,method=6)
        before=p.stat().st_size; after=target.stat().st_size
        if after>=before*.92:
            target.unlink(); continue
        mapping[p.as_posix()]=target.as_posix()
        stats.append({"original":p.as_posix(),"optimized":target.as_posix(),"before":before,"after":after})
    except Exception as exc:
        print("SKIP",p,exc)

# Production pages, scripts and data: leave tests, backups, workflow scripts,
# manifests and service workers alone. Exact local URL references only.
def production(p):
    n=p.name.lower()
    if p.suffix.lower() not in (".html",".css",".js",".json"):return False
    if p.parts[0] in (".github","scripts","docs","functions"):return False
    if any(x in n for x in ("backup","teste","test-","admin","manifest","service-worker","proposta","auditoria")):return False
    return p.is_file()

changes={}
for p in files:
    if not production(p):continue
    raw=p.read_text(encoding="utf-8")
    content=raw
    # Build URL aliases relative to this page, and root-relative links.
    import posixpath
    aliases={}
    for old,new in mapping.items():
        rel=posixpath.relpath(old,p.parent.as_posix())
        relnew=posixpath.relpath(new,p.parent.as_posix())
        for x,y in [(rel,relnew),("./"+rel,"./"+relnew),("/"+old,"/"+new)]:
            aliases[x]=y
            aliases[quote(x,safe="/")]=quote(y,safe="/")
            aliases[html.escape(x,quote=True)]=html.escape(y,quote=True)
    # Match complete quoted HTML/JS strings and CSS URLs. This avoids replacing
    # remote URLs or substrings of unrelated filenames.
    if aliases:
        keys=sorted(aliases,key=len,reverse=True)
        pattern=re.compile(r'(?P<q>["\x27])(?P<url>'+ '|'.join(map(re.escape,keys))+r')(?P=q)')
        content=pattern.sub(lambda m:m.group("q")+aliases[m.group("url")]+m.group("q"),content)
        pattern2=re.compile(r'url\(\s*(?P<url>'+ '|'.join(map(re.escape,keys))+r')\s*\)',re.I)
        # Case-sensitive filename lookup even though CSS url() is case-insensitive.
        content=pattern2.sub(lambda m:"url("+aliases[m.group("url")]+")" if m.group("url") in aliases else m.group(0),content)
    # Add native lazy loading to non-critical static images on the main page.
    # Keep the live player, initial branding and promo carousel eager.
    if p.as_posix()=="index.html":
        def lazy(m):
            tag=m.group(0)
            if re.search(r'\bloading\s*=',tag,re.I):return tag
            if re.search(r'\b(?:brand-logo|mini-artwork|live-program-photo|live-cover|promo-slide|future-slide|track-cover)\b',tag,re.I):return tag
            if re.search(r'\bid\s*=\s*["\x27](?:miniArtwork|liveArtwork|liveProgramPhoto)["\x27]',tag,re.I):return tag
            # Static gallery and podcast images can load when their section opens.
            return tag[:-1].rstrip()+" loading=\"lazy\" decoding=\"async\">"
        content=re.sub(r'<img\b[^>]*>',lazy,content,flags=re.I)
    if content!=raw:
        p.write_text(content,encoding="utf-8")
        changes[p.as_posix()]=len(content)-len(raw)

# Verify that every optimized copy exists and decodes. Keep all originals.
for item in stats:
    p=Path(item["optimized"])
    assert Path(item["original"]).is_file()
    with Image.open(p) as im: im.verify()
report={"images_examined":len(images),"images_optimized":len(stats),"original_bytes":sum(x["before"] for x in stats),"optimized_bytes":sum(x["after"] for x in stats),"files_updated":sorted(changes),"images":stats}
Path("docs/site-image-optimization-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="images"},indent=2))
assert stats, "No images optimized"
