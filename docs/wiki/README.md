# How to publish these pages

This directory is the GitHub wiki, one file per wiki page. Nothing here is served by the app; it exists so
the wiki can be updated from the repository, reviewed in a pull request, and checked by a test rather than
edited in a browser text box where nobody sees the diff.

`docs/WIKI.md` is a different thing and stays where it is: one long page for someone reading the repository
top to bottom. These are short pages for someone who arrived from a search result with one question.

## Publishing

```bash
git clone https://github.com/AGIFutureFoundation/AGI-Biotech-tool.wiki.git /tmp/biodao-wiki
cp docs/wiki/*.md /tmp/biodao-wiki/
rm /tmp/biodao-wiki/README.md          # this file is instructions, not a wiki page
cd /tmp/biodao-wiki && git add -A && git commit -m "Sync wiki from docs/wiki" && git push
```

The wiki repository has to be initialised once from the web interface — GitHub will not accept a push to
`<repo>.wiki.git` until the wiki has at least one page. Create any page in the browser, then push over it.

Or paste by hand: each filename is the page title with hyphens for spaces, which is exactly how GitHub
names wiki pages. `Home.md` is the landing page and `_Sidebar.md` is the navigation rail; both names are
GitHub conventions and must not be changed.

## Rules these pages follow

1. **No number without its source.** Every figure says which command produced it and when. A figure that
   cannot be re-measured right now is marked as carried forward, not restated as fresh.
2. **The weakest result is on the page.** The re-docking benchmark is 2 of 4 within 2 Å. That belongs in
   the wiki in the same size type as everything else.
3. **The score is unitless.** It is Vina-shaped and never written as kcal/mol.

`tests/wiki.test.mjs` enforces all three mechanically, plus link integrity and sidebar coverage. Run it
with `node --test tests/wiki.test.mjs` before pushing.
