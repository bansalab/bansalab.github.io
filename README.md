# bansalab.me — personal academic website

Personal/academic website for **Dr Aakash Bansal**, Lecturer in Applied
Electromagnetics, Loughborough University. Built as a single static page that
renders its publication list from `publications.json`, which is refreshed
automatically from Google Scholar every week.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The whole website (HTML/CSS/JS in one file). |
| `publications.json` | Publication data the page renders. **Auto-generated.** |
| `update_publications.py` | Scrapes Google Scholar and rewrites `publications.json`. |
| `requirements.txt` | Python dependency (`scholarly`). |
| `.github/workflows/update-publications.yml` | Weekly GitHub Action that runs the scraper and commits changes. |
| `og-image.png` | Social-share/link-preview card (referenced by Open Graph/Twitter tags). |
| `og-image.html` | Editable source for `og-image.png` (re-render to update). |
| `robots.txt` / `sitemap.xml` | SEO crawl + indexing helpers. |
| `cv.html` / `cv.pdf` | Optional ready-made CV (nav links to `resume.pdf`). |

## How the auto-update works

Google Scholar has no public API and blocks live browser requests, so the page
can't read it directly. Instead:

1. The GitHub Action runs every **Monday 06:00 UTC** (and can be run on demand
   from the **Actions** tab → *Update publications from Google Scholar* →
   *Run workflow*).
2. It runs `update_publications.py`, which uses the open-source
   [`scholarly`](https://github.com/scholarly-python-package/scholarly) library
   to read the profile `VBRbQlYAAAAJ` and write `publications.json` (titles,
   authors, venue, year, **live citation counts**, and a journal/conference tag).
3. If the file changed, the Action commits and pushes it. GitHub Pages then
   serves the updated list automatically.
4. If Scholar blocks the run (it sometimes rate-limits datacentre IPs), the step
   is allowed to fail and the **last good `publications.json` is kept** — the
   site never breaks.

The page sorts publications by year, marks the six most-cited as *Featured*, and
offers Featured / Journals / Conferences / All tabs. It shows a
"Last synced …" date under the section heading.

## One-time setup

1. **Push these files** to the repository that GitHub Pages serves (root of the
   `main` branch, or `/docs`, matching your Pages settings).
2. In the repo, go to **Settings → Actions → General → Workflow permissions**
   and select **Read and write permissions** (so the Action can commit the
   refreshed JSON). *(The workflow also requests this via `permissions:` but the
   repo setting must allow it.)*
3. Trigger the first run manually: **Actions → Update publications from Google
   Scholar → Run workflow**. Confirm `publications.json` updates.

That's it — after that it maintains itself weekly.

## Editing content

- **Text, research themes, consultancy, awards:** edit `index.html` directly.
- **Hero slideshow:** the hero shows an auto-rotating slideshow of schematic
  illustrations of selected papers (in the `class="slideshow"` block). To use
  real figure images instead, replace any slide's inline `<svg>…</svg>` with
  `<img src="images/your-figure.png" alt="…">` and keep the `<div class="cap">`
  caption. Timing is the `DELAY` value in the slideshow script.
- **CV:** the nav "CV" button links to `resume.pdf` — place your CV in the repo
  root with exactly that filename. (A ready-made `cv.pdf` / `cv.html` is also
  included if you'd rather use or adapt that one; if so, rename it to
  `resume.pdf` or change the link in `index.html`.)
- **Publications:** don't edit `publications.json` by hand — it is overwritten on
  each run. Add/curate work on your Google Scholar profile instead.

## Running the scraper locally (optional)

```bash
pip install -r requirements.txt
python update_publications.py      # rewrites publications.json
# add SCHOLARLY_USE_PROXY=1 if Google blocks your IP
```

## SEO

The page is optimised to rank for antenna/RF **consultancy** searches in your
research area:

- Keyword-focused `<title>`, meta description and keywords (mmWave, metasurface,
  RIS, 5G/6G, dielectric lens, satellite antenna, "consultant UK", etc.).
- **Structured data** (JSON-LD): `Person`, `ProfessionalService` (your
  consultancy, with service types and `knowsAbout`) and `WebSite` — this is what
  lets Google show rich results and understand the consultancy offering.
- Open Graph + Twitter cards with a branded `og-image.png` for strong link
  previews (better click-through from social/search).
- `robots.txt`, `sitemap.xml`, canonical URL and proper heading hierarchy.

**After deploying**, do these two things to actually get indexed/ranked:

1. Add the site to **Google Search Console** (verify ownership) and submit
   `https://www.bansalab.me/sitemap.xml`. Repeat with **Bing Webmaster Tools**.
2. Build a few authoritative inbound links (your Loughborough staff page,
   LinkedIn, ORCID, Google Scholar, ResearchGate) pointing at bansalab.me —
   backlinks remain the biggest ranking factor. Validate the structured data at
   [search.google.com/test/rich-results](https://search.google.com/test/rich-results).

## Notes

- Free scraping via `scholarly` is best-effort. If you find weekly runs are
  frequently blocked, the most reliable upgrade is SerpAPI's Google Scholar
  Author API (free tier ~100 searches/month) — the scraper can be swapped to use
  it with minimal changes.
