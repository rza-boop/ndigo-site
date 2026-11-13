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

# Legal entity (Rza, 13 Nov 2026): ndigo cartel is the brand and the site; the company is Dream Bigger Media Group, LLC.
LEGAL = "Dream Bigger Media Group, LLC"
CONTACT = "frank@frankwhitedealsdope.com"

def add_legal_footer():
    """Home is the only page with a footer. Name the company there and link the privacy page."""
    f = SITE / "index.html"; s = f.read_text()
    old = '<span id="sq"></span><span>ndigo cartel</span></div></footer>'
    assert old in s, "home footer changed"
    new = s.replace(old, f'<span id="sq"></span><span>ndigo cartel · a division of {LEGAL} · <a href="/privacy/" style="color:inherit">privacy</a></span></div></footer>')
    f.write_text(new)
    n = SITE / "404.html"  # the not-found page is the home page under another title
    n.write_text(new.replace("<title>ndigo cartel</title>", "<title>not found · ndigo cartel</title>", 1))

def build_privacy():
    """A plain text page in the home page's own styles (its :root, body, .led, .gut, menu and footer rules, copied from the
    built home so it follows any change to the comp). No new look."""
    home = (SITE / "index.html").read_text()
    def rule(pat):
        m = re.search(pat, home, flags=re.S); assert m, pat; return m.group(0)
    css = "\n".join([rule(r":root\{.*?\n\}"), "*{box-sizing:border-box}", rule(r"body\{margin:0;color:var\(--ink\).*?var\(--B\)\}"),
                     rule(r"body\.nopegs\{[^}]*\}"), "html,body{overflow-x:clip}", rule(r"\.led\{[^}]*\}"), rule(r"\.gut\{[^}]*\}"),
                     "\n".join(re.findall(r"nav\.menu[^{\n]*\{[^}]*\}", home)), "\n".join(re.findall(r"footer\.site[^{\n]*\{[^}]*\}", home)),
                     "main.legal{max-width:1180px;margin:0 auto;padding-block:16px}main.legal .in{padding:18px 20px;color:var(--ink)}"
                     "main.legal h1{font:400 34px/1.1 var(--vt);color:var(--G);margin:0 0 6px}main.legal h2{font:400 26px/1.2 var(--vt);color:var(--P);margin:22px 0 4px}"
                     "main.legal p,main.legal li{margin:6px 0;max-width:70ch}main.legal a{color:var(--G)}main.legal .d{color:var(--dim)}"])
    fonts = rule(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>')
    title, desc, url = "privacy · ndigo cartel", f"Privacy policy for ndigo cartel, a division of {LEGAL}.", ORIGIN + "/privacy/"
    body = f"""<nav class="menu gut" aria-label="Site"><div class="in led">
  <a href="/">ndigo cartel</a><a href="/books/">books</a><a href="/playlists/">playlists</a><a href="/games/">games</a><a href="/merch/">merch</a>
</div></nav>
<main class="legal gut"><div class="in led">
<h1>privacy policy</h1>
<p class="d">Effective 13 November 2026</p>
<p>ndigo cartel is a brand and division of {LEGAL}. This site, www.ndigocartel.com, and the games, books, playlists and merch published under the ndigo cartel name are operated by {LEGAL} ("we", "us").</p>
<h2>what we collect</h2>
<ul>
<li><b>Your email address</b>, only if you type it into the sign-up box on the games page. It is sent to our inbox through FormSubmit (formsubmit.co), which delivers the form.</li>
<li>Nothing else. This site has no accounts, no analytics, no advertising trackers, and sets no cookies of its own.</li>
</ul>
<h2>services this site loads</h2>
<ul>
<li>The site is hosted on GitHub Pages. GitHub may log your IP address to serve and protect the site.</li>
<li>Fonts are loaded from Google Fonts, so Google receives the request for them.</li>
<li>Links to Spotify, Substack and other sites take you to those sites, which have their own policies.</li>
</ul>
<h2>how we use your email</h2>
<p>To tell you about ndigo cartel games and releases. We do not sell it, rent it or trade it.</p>
<h2>removing your email</h2>
<p>Write to <a href="mailto:{CONTACT}">{CONTACT}</a> and we will remove it.</p>
<h2>games and apps</h2>
<p>As ndigo cartel games and apps are released, what each one collects will be listed on this page.</p>
<h2>children</h2>
<p>This site is not directed to children under 13, and we do not knowingly collect personal information from them.</p>
<h2>changes</h2>
<p>If this policy changes, the new version and its date will be posted here.</p>
<h2>contact</h2>
<p>{LEGAL}<br><a href="mailto:{CONTACT}">{CONTACT}</a></p>
</div></main>
<footer class="site gut"><div class="in led"><span></span><span>ndigo cartel · a division of {LEGAL}</span></div></footer>"""
    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" href="{FAV}">
<meta name="theme-color" content="#16141A">
{fonts}
<style>
{css}
</style>
</head><body class="nopegs">
{body}
</body></html>
"""
    d = SITE / "privacy"; d.mkdir(exist_ok=True); (d / "index.html").write_text(page); print("wrote privacy/index.html", len(page))

for k, (src, title, desc) in PAGES.items(): build(k, src, src, title, desc)
add_legal_footer()
build_privacy()
