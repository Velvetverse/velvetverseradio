#!/usr/bin/env python3
"""Browser smoke test and local transfer-size comparison for the review branch."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from urllib.parse import urlsplit, unquote
import json, os, re, shutil, sys
from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

ROOT=Path.cwd()
BASE=Path(sys.argv[1])
# Small display-only logo; original PNG remains untouched for app manifests.
with Image.open(ROOT/"icon-192.png") as src:
    im=ImageOps.exif_transpose(src)
    im.thumbnail((256,256),Image.Resampling.LANCZOS)
    im.save(ROOT/"icon-192.png.webp","WEBP",quality=90,method=6)
assert (ROOT/"icon-192.png.webp").stat().st_size < (ROOT/"icon-192.png").stat().st_size
report=json.loads((ROOT/"docs/site-image-optimization-report.json").read_text())
for name in report["files_updated"]:
    p=ROOT/name
    if p.suffix!=".html": continue
    s=p.read_text(encoding="utf-8")
    # Only display images, never web app manifest/favicon metadata.
    n=re.sub(r'(<img\b[^>]*?\bsrc\s*=\s*["\x27])((?:\.\./|\.\/|/)?icon-192\.png)(["\x27])',r'\1\2.webp\3',s,flags=re.I)
    if n!=s:p.write_text(n,encoding="utf-8")

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def server(root):
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root)))
    Thread(target=srv.serve_forever,daemon=True).start()
    return srv,f"http://127.0.0.1:{srv.server_port}"

def local_image(url,origin):
    return url.startswith(origin+"/") and re.search(r"\.(?:png|jpe?g|webp)(?:[?#]|$)",url,re.I)

def inspect(browser,origin,root,path,news=False):
    ctx=browser.new_context(viewport={"width":1440,"height":900},service_workers="block")
    # Test only local site assets. Radio streaming/remote APIs are not invoked.
    ctx.route("**/*",lambda route:route.continue_() if route.request.url.startswith(origin+"/") else route.abort())
    page=ctx.new_page()
    failed=[]
    page.on("response",lambda r:failed.append(r.url) if r.status>=400 and local_image(r.url,origin) else None)
    res=page.goto(origin+"/"+path,wait_until="load",timeout=45000)
    assert res and res.ok, f"Page failed: {path}"
    page.wait_for_timeout(300)
    assert page.title().strip(),f"Missing title: {path}"
    perf=page.evaluate("""() => performance.getEntriesByType('resource').filter(e=>/\\.(png|jpe?g|webp)([?#]|$)/i.test(e.name)&&e.name.startsWith(location.origin+'/')).map(e=>({name:e.name,bytes:e.encodedBodySize}))""")
    local=[x for x in page.eval_on_selector_all("img[src]","els=>els.map(e=>e.src)") if local_image(x,origin)]
    missing=[]
    for u in local:
        p=root/unquote(urlsplit(u).path).lstrip("/")
        if not p.is_file():missing.append(u)
    if news:
        page.locator("#featuredRead").click()
        assert page.locator("#articleView").is_visible(),"Featured article did not open"
        assert len(page.locator("#articleBody").inner_text())>500,"Featured article is unexpectedly short"
        page.locator("#backBtn").click()
        assert page.locator("#newsHome").is_visible(),"News navigation did not return"
        page.locator("#wxCanada").click()
        h1=page.locator(".vv-weather").bounding_box()["height"]
        page.locator("#wxPortugal").click()
        h2=page.locator(".vv-weather").bounding_box()["height"]
        assert abs(h1-h2)<1,"Weather panel height changes"
    ctx.close()
    return {"path":path,"requests":len(perf),"image_bytes":sum(x["bytes"] for x in perf),"missing":sorted(set(missing+failed))}

srv0,origin0=server(BASE)
srv1,origin1=server(ROOT)
paths=["index.html","noticias.html","schedule-oficial-embed.html","player.html","radio-app/index.html","backstage-legends.html","brasil-de-norte-a-sul.html","e-se.html","um-futuro-proximo.html","arquivos-do-inexplicavel.html","inside-velvetverse.html","discos-pedidos.html","top-5-latino.html"]
with sync_playwright() as pw:
    chrome=shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    browser=pw.chromium.launch(headless=True,executable_path=chrome or None,args=["--no-sandbox"])
    before=inspect(browser,origin0,BASE,"index.html")
    baseline_missing=set(before["missing"])
    results=[]
    for p in paths:
        result=inspect(browser,origin1,ROOT,p,news=(p=="noticias.html"))
        # Newly generated WebP links must all resolve. Old broken links, if any, are reported separately.
        assert not any(".webp" in u for u in result["missing"]),f"Broken optimized image: {p} {result['missing']}"
        results.append(result)
        print(p,result["requests"],result["image_bytes"],"bytes; missing:",len(result["missing"]))
    browser.close()
    after=results[0]
    assert after["image_bytes"] < before["image_bytes"],"Home image transfer did not improve"
    output={"before_home":before,"after_home":after,"pages":results,"display_logo_bytes_before":(ROOT/"icon-192.png").stat().st_size,"display_logo_bytes_after":(ROOT/"icon-192.png.webp").stat().st_size}
    (ROOT/"docs/site-browser-performance-report.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("HOME before/after",before["image_bytes"],after["image_bytes"])
srv0.shutdown();srv1.shutdown()
