# ndigocartel.com

Static site on GitHub Pages (repo rza-boop/ndigo-site). www.ndigocartel.com is the main address and the bare domain redirects to it. DNS is at Namecheap: the apex has the four GitHub Pages A records and www is a CNAME to rza-boop.github.io. Every setHosts call must pass `EmailType=FWD` (Namecheap email forwarding), and the records from before go-live are in `_build/namecheap-before.xml`.

- Pages: `/` home (TV wall), `/books/`, `/playlists/`, `/games/`, `/merch/`. Each one is the approved review comp with its review bar hidden.
- To rebuild after changing a comp: put the comp HTML in `_build/src/` (home.html, books.html, playlists.html, games.html, merch.html), run `python3 _build/build_site.py _build/src`, copy index.html to 404.html, then commit and push.
- The games sign-up posts to FormSubmit, going to frank@frankwhitedealsdope.com (the same inbox as the FWD list) with the subject "ndigo cartel · games sign-up".
- The merch checkout is disabled ("booth opens soon") until the ndigo cartel Fourthwall shop exists.
