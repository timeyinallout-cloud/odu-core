#!/usr/bin/env python3
"""Generate the knowledge base site into ``site/``.

    python3 scripts/build_kb_site.py

Static HTML, one permalink per figure, no runtime and no build chain. A
preservation project should still open in a browser in twenty years, and every
dependency is a way that stops being true.

Content comes only from the ``publishable_*`` views, so publication is
default-deny: a record appears here only if it is marked published, is not
restricted, its source permits reproduction, and its contributors still consent.
"""

from __future__ import annotations

import html
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core import all_odu, spec_version  # noqa: E402
from odu_core.kb import SCHEMA_PATH, coverage, stats  # noqa: E402
from odu_core.types import Odu  # noqa: E402

DB_PATH = ROOT / "kb" / "odu.db"
OUT = ROOT / "site"

STYLE = """
:root {
  --bg:#fbf9f6; --fg:#1c1a17; --dim:#6b6560; --line:#e0dad2; --card:#fff;
  --accent:#7a4b1e; --mono:ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#16140f;--fg:#ece6dd;--dim:#9a938a;--line:#2f2a23;--card:#1e1b16;--accent:#d9a566}
}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.25rem 4rem;background:var(--bg);color:var(--fg);
  font:16px/1.65 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:60rem;margin:0 auto}
a{color:var(--accent)}
h1{font-size:1.7rem;margin:0 0 .25rem;letter-spacing:-.01em}
h2{font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
  margin:2rem 0 .75rem;font-weight:600}
.sub{color:var(--dim);margin:0 0 1.5rem}
.crumb{font-size:.85rem;color:var(--dim);margin-bottom:1.25rem}
.note{border-left:3px solid var(--accent);background:var(--card);padding:.75rem 1rem;
  margin:0 0 1.75rem;font-size:.9rem;color:var(--dim)}
.note strong{color:var(--fg)}
#q{width:100%;padding:.6rem .75rem;font-size:.95rem;background:var(--card);
  color:var(--fg);border:1px solid var(--line);border-radius:6px;margin-bottom:1rem}
.grid{display:grid;gap:.4rem;grid-template-columns:repeat(auto-fill,minmax(9.5rem,1fr))}
.cell{display:block;padding:.5rem .6rem;border:1px solid var(--line);border-radius:6px;
  background:var(--card);text-decoration:none;color:var(--fg);font-size:.78rem}
.cell:hover{border-color:var(--accent)}
.cell .b{font-family:var(--mono);font-size:.68rem;color:var(--dim);display:block}
.cell.has::after{content:"●";color:var(--accent);font-size:.6rem;margin-left:.3rem}
table{width:100%;border-collapse:collapse;font-size:.9rem}
td,th{text-align:left;padding:.4rem .6rem .4rem 0;border-bottom:1px solid var(--line);
  vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:.8rem;white-space:nowrap}
pre.fig{font-family:var(--mono);font-size:.8rem;line-height:1.3;background:var(--card);
  border:1px solid var(--line);border-radius:6px;padding:.9rem 1.1rem;display:inline-block;margin:0}
.empty{color:var(--dim);font-style:italic;font-size:.92rem}
.pair{display:flex;gap:1.5rem;flex-wrap:wrap;align-items:flex-start}
.stat{font-family:var(--mono);font-size:.85rem;color:var(--dim)}
.ways{font-size:.95rem;color:var(--dim);margin:.4rem 0 1rem}
.ways a{color:var(--accent)}
footer{color:var(--dim);font-size:.82rem;margin-top:3rem;border-top:1px solid var(--line);
  padding-top:1rem}
code{font-family:var(--mono);font-size:.85em}
"""

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="{root}style.css">
</head><body><main>
{body}
<footer>{footer}</footer>
</main>{script}</body></html>
"""

FOOTER = (
    'Generated from <code>data/principal_odu.json</code>, spec {spec}. '
    'All 16 principal figures verified against Bascom (1969), Table 1 p. 4 and '
    'Table 3 col. B p. 48. '
    'Content appears only where a citable source exists — see '
    '<a href="{root}index.html">the index</a> for coverage.'
    '<br><br>Archived at '
    '<a href="https://doi.org/10.5281/zenodo.21743991" rel="noopener">'
    'doi:10.5281/zenodo.21743991</a> — please cite Bascom alongside it, as this '
    'dataset is a transcription rather than a discovery.'
)


def e(text: object) -> str:
    return html.escape(str(text), quote=True)


def show(path: Path) -> str:
    """Path relative to the repo when it is inside it, absolute otherwise."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def figure_block(odu: Odu) -> str:
    return f'<pre class="fig">{e(odu.figure())}</pre>'


def rows(pairs: list[tuple[str, str]]) -> str:
    body = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in pairs)
    return f"<table>{body}</table>"


def render_odu_page(odu: Odu, db: sqlite3.Connection | None) -> str:
    verses: list[sqlite3.Row] = []
    notes: list[sqlite3.Row] = []
    recordings: list[sqlite3.Row] = []
    if db is not None:
        verses = db.execute(
            "SELECT * FROM publishable_verse WHERE odu_byte=? ORDER BY sequence, id",
            (odu.byte,),
        ).fetchall()
        recordings = db.execute(
            "SELECT r.*, s.title AS src_title, s.author AS src_author "
            "FROM publishable_recording r JOIN source s ON s.id=r.source_id "
            "WHERE r.odu_byte=? ORDER BY r.id",
            (odu.byte,),
        ).fetchall()
        notes = db.execute(
            "SELECT n.*, s.title AS src_title, s.author AS src_author, s.year AS src_year "
            "FROM publishable_note n JOIN source s ON s.id=n.source_id "
            "WHERE n.odu_byte=? ORDER BY n.id",
            (odu.byte,),
        ).fetchall()

    # An attested contracted name is the traditional name of the figure, so it
    # belongs beside the descriptive one rather than buried under commentary.
    attested = [n for n in notes if n["kind"] == "alternative-name"]

    detail = [
        ("Right leg", f"<span lang='yo'>{e(odu.right.name)}</span> <span class='stat'>({odu.right.bits})</span>"),
        ("Left leg", f"<span lang='yo'>{e(odu.left.name)}</span> <span class='stat'>({odu.left.bits})</span>"),
        ("Slug", f"<code>{e(odu.slug)}</code>"),
        ("Seniority", f"{odu.seniority_rank} of 256"),
        ("Méjì", "yes" if odu.is_meji else "no"),
    ]
    if attested:
        detail.insert(0, (
            "Attested name",
            " · ".join(
                f"<span lang='yo'>{e(n['text'])}</span> <span class='stat'>({e(n['src_author'] or n['src_title'])} "
                f"{e(n['src_year'] or '')})</span>"
                for n in attested
            ),
        ))

    parts = [
        '<div class="crumb"><a href="../index.html">← all 256 figures</a></div>',
        f'<h1 lang="yo">{e(odu.name)}</h1>',
        f'<p class="sub">Byte {odu.byte} · 0x{odu.byte:02X} · {odu.bits}</p>',
        '<div class="pair">',
        figure_block(odu),
        rows(detail),
        "</div>",
        "<h2>Verses</h2>",
    ]

    if verses:
        for v in verses:
            text = e(v["yoruba_text"]) if v["yoruba_text"] else "<em>cited only</em>"
            ref = e(v["page_reference"] or "")
            parts.append(f"<p>{text}<br><span class='stat'>{ref}</span></p>")
    else:
        parts.append(
            '<p class="empty">No verse has been recorded for this figure yet. '
            "Entries require a citable source.</p>"
        )

    parts.append("<h2>Recitations</h2>")
    if recordings:
        for r in recordings:
            who = e(r["src_author"] or r["src_title"])
            parts.append(
                f'<p><a href="{e(r["path"])}" rel="noopener noreferrer nofollow" '
                f'target="_blank">{who}</a><br>'
                f'<span class="stat">a recitation of this figure — linked, not hosted; '
                f'attribution confirmed, the reciter\'s standing is not established'
                f'</span></p>'
            )
    else:
        parts.append('<p class="empty">No recitation cited for this figure yet.</p>')

    parts.append("<h2>Notes</h2>")
    other = [n for n in notes if n["kind"] != "alternative-name"]
    if other:
        for n in other:
            cite = " ".join(
                str(x) for x in (n["src_author"], n["src_year"]) if x
            )
            parts.append(
                f"<p>{e(n['text'])}<br><span class='stat'>{e(n['kind'])} — "
                f"{e(cite or n['src_title'])}</span></p>"
            )
    else:
        parts.append('<p class="empty">No sourced commentary yet.</p>')

    return PAGE.format(
        title=f"{odu.name} — Odù knowledge base",
        root="../",
        body="\n".join(parts),
        footer=FOOTER.format(spec=spec_version(), root="../"),
        script="",
    )


def render_index(db: sqlite3.Connection | None) -> str:
    counts = coverage(db) if db is not None else {b: 0 for b in range(256)}
    summary = stats(db) if db is not None else None

    cells = []
    for odu in all_odu():
        has = " has" if counts.get(odu.byte) else ""
        cells.append(
            f'<a class="cell{has}" href="odu/{e(odu.slug)}.html" '
            f'data-s="{e(odu.slug)} {e(odu.name.lower())} {odu.byte} {odu.bits}">'
            f'<span lang="yo">{e(odu.name)}</span><span class="b">{odu.byte} · {odu.bits}</span></a>'
        )

    if summary:
        stat_line = (
            f"{summary['figures_covered']} of 256 figures have entries · "
            f"{summary['verses']} verses ({summary['verses_publishable']} publishable) · "
            f"{summary['sources']} sources"
        )
    else:
        stat_line = "No database yet — run <code>python3 scripts/ingest.py</code>."

    body = f"""
<h1>Odù knowledge base</h1>
<p class="sub">The 256 figures of Ifá, each a byte. Two legs, four lines, one mark or two.</p>
<div class="note">
  <strong>The corpus starts empty, deliberately.</strong> Nothing is stored without a
  citable source, and no verse here was generated. Ẹsẹ Ifá is living practice — some of it
  is initiation-restricted, and much published material remains in copyright, so records
  may hold a page reference rather than reproduced text. Entries appear as they are sourced.
</div>
<p class="stat">{stat_line}</p>
<p class="ways">
  Also here:
  <a href="art.html">the 256 figures as generative art</a> &middot;
  <a href="encoder/">turn any text into Odù</a> &middot;
  <a href="verify/">check two files match</a> &middot;
  <a href="https://github.com/timeyinallout-cloud/odu-core">the data and the code</a>
</p>
<input id="q" type="search" placeholder="Filter by name, slug, byte, or bit pattern…"
       autocomplete="off" aria-label="Filter figures">
<div class="grid" id="g">{''.join(cells)}</div>
"""
    script = """<script>
const q=document.getElementById('q'),cells=[...document.querySelectorAll('.cell')];
const fold=s=>s.normalize('NFD').replace(/\\p{Mn}/gu,'').toLowerCase();
q.addEventListener('input',()=>{const t=fold(q.value.trim());
  cells.forEach(c=>{c.style.display=!t||fold(c.dataset.s).includes(t)?'':'none'})});
</script>"""

    return PAGE.format(
        title="Odù knowledge base — the 256 figures",
        root="",
        body=body,
        footer=FOOTER.format(spec=spec_version(), root=""),
        script=script,
    )


def main() -> int:
    db: sqlite3.Connection | None = None
    if DB_PATH.exists():
        db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
    else:
        print(f"no database at {show(DB_PATH)} — building an empty site")
        if not SCHEMA_PATH.exists():
            print("schema missing too; run scripts/ingest.py first", file=sys.stderr)
            return 1

    (OUT / "odu").mkdir(parents=True, exist_ok=True)
    (OUT / "style.css").write_text(STYLE.strip() + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(db), encoding="utf-8")

    for odu in all_odu():
        (OUT / "odu" / f"{odu.slug}.html").write_text(
            render_odu_page(odu, db), encoding="utf-8"
        )

    # A machine-readable index, so the site is not the only way back to the data.
    (OUT / "index.json").write_text(
        json.dumps(
            {
                "specVersion": spec_version(),
                "figures": [
                    {"byte": o.byte, "slug": o.slug, "name": o.name,
                     "url": f"odu/{o.slug}.html"}
                    for o in all_odu()
                ],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    if db is not None:
        db.close()
    print(f"wrote {show(OUT)}/ — 256 figure pages, index, and index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
