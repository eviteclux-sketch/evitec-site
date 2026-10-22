# Cherche des photos libres sur Wikimedia Commons et télécharge des vignettes + licences (exécuté par GitHub Actions).
import json, os, re, sys, urllib.parse, urllib.request
UA = {"User-Agent": "rebond-images/1.0 (contact: eviteclux@gmail.com)"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
cfg = json.load(open("rebond/img/requetes.json"))
os.makedirs("rebond/img/cand", exist_ok=True)
out = {}
for q in cfg.get("recherches", []):
    p = {"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":"6","gsrlimit":str(cfg.get("n",8)),
         "prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":"480"}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)))
    for pg in sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = (pg.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lic = (m.get("LicenseShortName") or {}).get("value", "")
        if not re.search(r"CC0|Public domain|CC BY", lic, re.I): continue
        if ii.get("width", 0) < 1200: continue
        key = "c%03d" % len(out)
        try: open(f"rebond/img/cand/{key}.jpg", "wb").write(get(ii["thumburl"]))
        except Exception as e: print("échec", e); continue
        out[key] = {"q": q, "titre": pg["title"], "page": ii.get("descriptionurl"), "url": ii.get("url"), "w": ii.get("width"), "h": ii.get("height"),
                    "licence": lic, "auteur": re.sub("<[^>]+>", "", (m.get("Artist") or {}).get("value", "")).strip()[:120]}
for key, name in cfg.get("garder", {}).items():
    # télécharge la grande version d'une image choisie (clé = nom final, valeur = titre File:...)
    p = {"action":"query","format":"json","titles":name,"prop":"imageinfo","iiprop":"url","iiurlwidth":"1800"}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)))
    ii = list(d["query"]["pages"].values())[0]["imageinfo"][0]
    open(f"rebond/img/{key}.jpg", "wb").write(get(ii["thumburl"])); print("gardé", key)
json.dump(out, open("rebond/img/cand/index.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "candidates")
