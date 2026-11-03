"""Build the ndigocartel.com static site from the approved review comps.

Each comp is a claude.ai artifact page: a grey review bar (Pick/Revise/Drop + notes), the page itself, and a
layout-study tag. This keeps the page and its scripts exactly as approved, hides the review chrome (the scripts
still find their elements, so nothing breaks), wraps it in a real <head>, and points links at the site's own paths.
Run: python3 _build/build_site.py <src-dir>   (src-dir holds home.html books.html playlists.html games.html merch.html)
"""
import re, sys, pathlib
SITE = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1])
ORIGIN = "https://www.ndigocartel.com"
ART = {"Tcf7vc2xDHtRjMUMXt65XB": "/books/", "SwnbmaBhrRVhnnjAok44NZ": "/playlists/",
       "5a9zgLhNEjrpqKJKQayzqy": "/games/", "5NXNwy6ttcot47ZUqQ9M6g": "/merch/"}
PAGES = {  # src, out dir, title, description
 "home":      ("", "ndigo cartel", "ndigo cartel. books, playlists, games and merch."),
 "books":     ("books/", "books · ndigo cartel", "Overtime editions and illustrated classics from ndigo cartel."),
 "playlists": ("playlists/", "playlists · ndigo cartel", "Spin the ndigo cartel playlists and open them on Spotify."),
 "games":     ("games/", "games · ndigo cartel", "LOR HEX and The Tester, coming soon from ndigo cartel."),
 "merch":     ("merch/", "merch · ndigo cartel", "ndigo cartel merch. Exclusive, never on Amazon."),
}
FAV = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 9'%3E%3Crect width='9' height='9' fill='%2316141A'/%3E"
       "%3Cpath fill='%23E100FF' d='M1 3h1v4H1zM2 3h1v1H2zM3 3h2v1H3zM5 4h1v3H5z'/%3E%3Crect x='7' y='6' width='1' height='1' fill='%237CFF4F'/%3E%3C/svg%3E")
HIDE = "<style>.review,.tag{display:none!important}</style>"
FORM = "https://formsubmit.co/ajax/frank@frankwhitedealsdope.com"

def strip_skeleton(s):
    if s.lstrip().lower().startswith("<!doctype"):
        s = s[s.index("<body>") + len("<body>"):]
        s = re.sub(r"</body></html>\s*$", "", s)
    return s

def build(key, src, out, title, desc):
    s = strip_skeleton((SRC / f"{key}.html").read_text())
    s = re.sub(r"<title>.*?</title>\s*", "", s, count=1, flags=re.S)
    s = re.sub(r'<meta charset="utf-8">\s*|<meta name="claude:viewport-fit-sides"[^>]*>\s*', "", s)
    # review notes are internal: empty the description, keep the elements the scripts look up
    s = re.sub(r'(<div class="what">).*?(</div>)', r"\1\2", s, count=1, flags=re.S)
    s = re.sub(r'(<div class="tag">).*?(</div>)', r"\1\2", s, count=1, flags=re.S)
    s = re.sub(r'<div class="footer">layout study[^<]*</div>\s*', "", s)  # merch comp's study line
    s = s.replace('<a href="#">ndigo cartel</a>', '<a href="/">ndigo cartel</a>')
    for aid, path in ART.items():
        s = s.replace(f'href="https://claude.ai/artifact/{aid}" target="_blank" rel="noopener"', f'href="{path}"')
        s = s.replace(f"https://claude.ai/artifact/{aid}", path)
    if key == "games":  # the comp saved sign-ups to the artifact db; on the site they go to the list inbox
        old = 'const db=await (window.claude?.use?.("db") ?? null); if(db) await db.collection("signups").add({email:v,at:Date.now(),from:"games"});'
        assert old in s, "games sign-up code changed"
        s = s.replace(old, f'const r=await fetch("{FORM}",{{method:"POST",headers:{{"Content-Type":"application/json",Accept:"application/json"}},body:JSON.stringify({{email:v,_subject:"ndigo cartel · games sign-up",from:"ndigocartel.com/games"}})}}); if(!r.ok) throw new Error(r.status);')
    s = s.replace("= $1 usd · placeholder prints and counts", "= $1 usd · booth opens soon")
    url = ORIGIN + "/" + src
    head = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" href="{FAV}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ndigo cartel">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16141A">
<style>body{{margin:0}}img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}</style>
{HIDE}
</head><body>
"""
    d = SITE / src; d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(head + s.strip() + "\n</body></html>\n")
    print("wrote", (d / "index.html").relative_to(SITE), len(s))

for k, (src, title, desc) in PAGES.items(): build(k, src, src, title, desc)
