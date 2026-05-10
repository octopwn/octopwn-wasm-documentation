# Documentation generators

Helper scripts that derive parts of the documentation directly from the
OctoPwn source tree and the live mkdocs nav. Everything here is meant
to be re-runnable on every release so the docs cannot drift from the
code.

Both scripts are pure Python with a single non-stdlib dependency
(`PyYAML` for the `llms.txt` generator, already pulled in by mkdocs).
Run them from the repository root with the docs venv activated:

```bash
cd octopwn-wasm-documentation
source .venv/bin/activate
python scripts/generate_flowgraph_reference.py
python scripts/generate_llms_txt.py --full
```

---

## `generate_flowgraph_reference.py`

**Output:** `docs/plugins/automations/flowgraph/blocks/*.md` (one page
per block category, plus `index.md`).

**Input:** `octopwn/enterprise/flowgraph/registry.py` — the in-tree
`BLOCK_REGISTRY` dict — imported live from the sibling `octopwn` repo
checkout.

### What it does

Walks `BLOCK_REGISTRY` and, for every block, emits a structured
markdown section containing:

- a one-line description from the registry,
- the block's category badge,
- a table of **input ports** (name, wire type, required flag,
  description),
- a table of **output ports** (same shape),
- a table of **parameters** (name, type, default, choices,
  description) when the block exposes any,
- the block's **output schema** (field name, type, description) when
  one is declared,
- MITRE **ATT&CK** technique badges when the block is mapped to one.

Blocks are grouped into stable categories — `Sources & prompts`,
`Queues & sinks`, `CredMux`, `Filters & gates`, `Scanners`, `Sessions`,
`Commands`, `Attacks`, `Enumeration`, `Transforms`, `Script`,
`Boundaries`, `Composites`, `Consoles & taps` — and each category is
written to its own markdown file with a hand-curated intro paragraph.

The generated pages carry an `AUTO-GENERATED — DO NOT EDIT` banner at
the top together with the exact command to regenerate them. The
companion `blocks/index.md` is also auto-generated and uses the
`summary` field embedded in the script's `PAGES` table as the one-line
description for each category.

### Configuration knobs

There are no CLI flags; behaviour is driven by two structures inside
the script:

- `PAGES` — list of `{file, title, categories, intro, summary}` dicts.
  Edit this when adding a new category or rewording an intro.
- `CATEGORY_LABELS` — pretty labels used for the badges and group
  headings.

### When to run

- After **any** edit to `octopwn/enterprise/flowgraph/registry.py`
  (new block, renamed port, changed default, new ATT&CK mapping).
- Before tagging a docs release.

The script is idempotent: if nothing changed in the registry, the
output files will be byte-identical to what is already committed.

### Layout assumptions

The script expects the `octopwn` source tree to live as a sibling of
`octopwn-wasm-documentation/`:

```
parent/
├── octopwn/                       ← OctoPwn source repo
└── octopwn-wasm-documentation/    ← this repo
    └── scripts/generate_flowgraph_reference.py
```

If your checkout layout differs, pass `--octopwn-root /path/to/octopwn`.

---

## `generate_llms_txt.py`

**Output:**
- `docs/llms.txt` — the curated, machine-readable index that follows
  the [llms.txt convention](https://llmstxt.org/).
- `docs/llms-full.txt` — full concatenation of every documentation
  page in nav order (only with `--full`).

**Input:** `mkdocs.yml` (nav order, site metadata) and every markdown
file the nav references.

### Why this exists

LLM-powered assistants and agents increasingly look for a top-level
`llms.txt` to discover what a documentation site contains. Without
one they fall back to crawling the rendered HTML, which is wasteful
and often confused by the Material theme's nav drawer. A small,
explicit `llms.txt` lets them:

- know the site exists (a single file at a well-known path),
- see a one-line summary for every page,
- pick exactly the pages relevant to a user's question and fetch only
  those.

`llms-full.txt` is the "swallow the whole product" companion file: a
single ~1 MB plain-text bundle of all pages, useful for offline
question answering and for shipping the docs to local models with
large context windows.

### What it does

1. Loads `mkdocs.yml` (with a tolerant YAML loader that ignores
   mkdocs-specific tags such as `!ENV`).
2. Walks the `nav` tree recursively, flattening it into an ordered
   list of `(section, subsection, title, doc_path)` tuples — nav
   order is preserved end-to-end.
3. For each page, parses the markdown and extracts the **first
   plain-prose paragraph**, skipping:
   - `<!-- AUTO-GENERATED -->` HTML comment banners,
   - fenced code blocks (including mermaid),
   - headings, tables, bullet lists, blockquotes,
   - `!!! note` / `??? warning` admonition blocks,
   - image-only paragraphs.
   Inline markdown (links, code spans, bold, italic, images) is
   stripped before clipping the result to ~240 characters. The
   underscore-emphasis regex is word-boundary-aware so identifiers
   like `SOURCE_NEW` and `OPEN_SESSION_<CLIENT>` survive intact.
4. Writes `docs/llms.txt` with:
   - the site name from `mkdocs.yml`,
   - a short OctoPwn-specific intro paragraph,
   - per-section `##` headings (and `###` subsections for groups like
     `Recipes` and `Block reference`),
   - one `- [Title](url): summary` line per page.
5. With `--full`, also writes `docs/llms-full.txt`: every page's full
   body concatenated in nav order, each prefixed with a `---` divider
   and a header carrying the section path, page title and canonical
   URL.

### URL construction

The generator honours `use_directory_urls` from `mkdocs.yml`:

- `use_directory_urls: true`  → `…/page/` (mkdocs default).
- `use_directory_urls: false` → `…/page.html` (current OctoPwn setup).

The base URL is taken from `site_url` in `mkdocs.yml` when present, or
the `--base-url` flag, otherwise falls back to
`https://docs.octopwn.com`.

### Flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--mkdocs-yml PATH`   | `../mkdocs.yml` relative to the script | Use a different mkdocs config. |
| `--base-url URL`      | `site_url` from config, else `https://docs.octopwn.com` | Override the public base URL used in links. |
| `--full`              | off | Also emit `docs/llms-full.txt`. |

### When to run

- After **any** change to the mkdocs nav (`mkdocs.yml` `nav:` block).
- After adding or renaming a documentation page.
- Before tagging a docs release.

Both outputs are deterministic given the same input, so running the
generator twice in a row produces no diff.

### Discoverability hooks

Just generating the files isn't enough — search engines and LLM
crawlers need to be able to find them. Three hooks are wired up so
both files are discoverable from any page of the rendered site:

1. **Built into the deployed site root.** Both files live in
   `docs/` so mkdocs copies them as-is into `site/llms.txt` and
   `site/llms-full.txt`, served at the canonical well-known paths
   `https://docs.octopwn.com/llms.txt` and `/llms-full.txt`.
2. **Visible link on the homepage.** `docs/index.md` carries a
   "For LLMs & AI agents" section with hyperlinks to both files,
   which gives Google's crawler a real `<a href>` to follow.
3. **`<link rel="alternate">` tags in every page.** The template
   `overrides/main.html` extends Material's `extrahead` block and
   injects two `<link rel="alternate" type="text/plain">` tags
   pointing at `/llms.txt` and `/llms-full.txt`, following the
   advertisement convention from llmstxt.org. The override is
   wired up by `theme.custom_dir: overrides` in `mkdocs.yml`.

If you rename the files or change their on-disk location, all three
hooks above must be updated to match.

### Sanity check

After regenerating, the simplest smoke test is to confirm `mkdocs
build --strict` is happy, that both files end up in the built site
root, and that the link count in `llms.txt` matches the number of
leaves in the nav:

```bash
python scripts/generate_llms_txt.py --full
mkdocs build --strict
test -f site/llms.txt && test -f site/llms-full.txt && echo "ok"
grep -c '^- \[' docs/llms.txt
grep -c 'rel="alternate".*llms' site/index.html  # should print 2
```

The grep count should match the number of leaf `.md` entries in
`mkdocs.yml`'s nav.

---

## Release checklist

When cutting a documentation release:

1. Pull / update both `octopwn` and `octopwn-wasm-documentation`
   working copies.
2. `python scripts/generate_flowgraph_reference.py`
3. `python scripts/generate_llms_txt.py --full`
4. `mkdocs build --strict` — must pass with zero warnings beyond the
   expected absolute-image-link `INFO` notes.
5. Commit the regenerated `docs/plugins/automations/flowgraph/blocks/`
   directory, `docs/llms.txt` and `docs/llms-full.txt` together with
   any prose edits.
