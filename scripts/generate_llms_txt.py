#!/usr/bin/env python3
"""
Generate ``docs/llms.txt`` (and optionally ``docs/llms-full.txt``) from
the live ``mkdocs.yml`` navigation.

``llms.txt`` follows the convention described at https://llmstxt.org/:
a single short markdown file that lets LLM-powered assistants discover
the documentation site, see what it contains, and pick the right pages
to fetch — without having to crawl the whole tree.

The generator:

  1. Reads ``mkdocs.yml`` for the site name, description, repo / site
     URLs and full nav tree.
  2. Walks the nav recursively, collecting every leaf markdown page in
     nav order.
  3. For each leaf, extracts a one-line summary from the page's first
     plain-prose paragraph (skipping AUTO-GENERATED banners, code
     fences, admonitions, mermaid blocks and `>` callouts).
  4. Writes ``docs/llms.txt`` with site metadata, an intro paragraph
     and per-section bulleted lists of links + summaries.
  5. With ``--full`` also writes ``docs/llms-full.txt``: every page
     concatenated in nav order, separated by a clear header. This is
     the "swallow the whole product" file for LLMs with enough
     context to take it.

Usage:
    cd octopwn-wasm-documentation
    python scripts/generate_llms_txt.py                    # llms.txt only
    python scripts/generate_llms_txt.py --full             # plus llms-full.txt
    python scripts/generate_llms_txt.py --base-url URL ... # override site URL
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
DOCS_ROOT = HERE.parent
MKDOCS_YML = DOCS_ROOT / 'mkdocs.yml'

# Fallback site URL — overridden by ``site_url`` in mkdocs.yml or the
# ``--base-url`` CLI flag. We hardcode the canonical one here because
# the current mkdocs.yml does not set ``site_url`` and we still want a
# usable default.
DEFAULT_BASE_URL = 'https://docs.octopwn.com'


# ---------------------------------------------------------------------------
# mkdocs.yml parsing
# ---------------------------------------------------------------------------

# mkdocs uses a small set of custom YAML tags (``!ENV``, ``!!python/name:…``)
# that PyYAML's safe loader does not know about. We don't need to
# evaluate them — we just need the nav — so the cleanest approach is a
# loader that returns the raw scalar for any unknown tag.
class _MkDocsLoader(yaml.SafeLoader):
    pass


def _unknown_tag(loader, tag_suffix, node):  # noqa: ARG001
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


_MkDocsLoader.add_multi_constructor('', _unknown_tag)
_MkDocsLoader.add_multi_constructor('!', _unknown_tag)


def _load_mkdocs_config(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.load(f, Loader=_MkDocsLoader) or {}
    return cfg


# ---------------------------------------------------------------------------
# Nav walking
# ---------------------------------------------------------------------------

class NavLeaf:
    """A single page referenced from the nav."""

    __slots__ = ('section', 'subsection', 'title', 'doc_path')

    def __init__(self, section: str, subsection: str, title: str, doc_path: str):
        self.section = section          # top-level nav group ("Clients")
        self.subsection = subsection    # nested group, if any ("Recipes")
        self.title = title              # the leaf's nav label
        self.doc_path = doc_path        # path relative to docs_dir, e.g. "user-guide/target.md"


def _walk_nav(nav: list, *, section: str = '', subsection: str = '') -> list[NavLeaf]:
    """Flatten a mkdocs nav structure into a list of NavLeaf in nav order."""
    out: list[NavLeaf] = []
    for entry in nav or []:
        if not isinstance(entry, dict) or not entry:
            continue
        for label, value in entry.items():
            if isinstance(value, str):
                doc_path = value.lstrip('./')
                out.append(NavLeaf(section or label, subsection, label, doc_path))
            elif isinstance(value, list):
                new_section    = section or label
                new_subsection = label if section else ''
                out.extend(_walk_nav(value, section=new_section, subsection=new_subsection))
    return out


# ---------------------------------------------------------------------------
# Summary extraction
# ---------------------------------------------------------------------------

# Lines / blocks that should never contribute to the summary
_RE_HTML_COMMENT_OPEN  = re.compile(r'<!--')
_RE_HTML_COMMENT_CLOSE = re.compile(r'-->')
_RE_FENCE              = re.compile(r'^\s*```')
_RE_ADMONITION_START   = re.compile(r'^\s*(?:!!!|\?\?\?)\s')
_RE_HEADING            = re.compile(r'^\s*#{1,6}(\s|$)')
_RE_TABLE_LINE         = re.compile(r'^\s*\|')
_RE_BULLET             = re.compile(r'^\s*[-*+]\s')
_RE_BLOCKQUOTE         = re.compile(r'^\s*>\s')

# Markdown noise we want to strip from the chosen paragraph before
# emitting it as a summary.
_RE_MD_IMAGE   = re.compile(r'!\[([^\]]*)\]\([^)]*\)')
_RE_MD_LINK    = re.compile(r'\[([^\]]+)\]\([^)]*\)')
_RE_MD_CODE    = re.compile(r'`([^`]+)`')
_RE_MD_BOLD    = re.compile(r'\*\*([^*]+)\*\*')
_RE_MD_ITAL    = re.compile(r'\*([^*]+)\*')
_RE_MD_UNDER   = re.compile(r'(?<!\w)_([^_\s][^_]*?[^_\s]|[^_\s])_(?!\w)')
_RE_WHITESPACE = re.compile(r'\s+')


def _strip_inline_markdown(text: str) -> str:
    text = _RE_MD_IMAGE.sub(r'\1', text)
    text = _RE_MD_LINK.sub(r'\1', text)
    text = _RE_MD_CODE.sub(r'\1', text)
    text = _RE_MD_BOLD.sub(r'\1', text)
    text = _RE_MD_ITAL.sub(r'\1', text)
    text = _RE_MD_UNDER.sub(r'\1', text)
    return _RE_WHITESPACE.sub(' ', text).strip()


def _iter_prose_paragraphs(content: str):
    """Yield successive plain-prose paragraphs from a markdown document.

    Skips every non-prose block (HTML comments / banners, code fences,
    mermaid blocks, admonition blocks, headings, tables, blockquotes,
    bullet lists). Each yielded paragraph is a single string with
    inline markdown already stripped.
    """
    in_comment = False
    in_fence   = False
    in_admon   = False

    para: list[str] = []

    def flush() -> str:
        if not para:
            return ''
        joined = _strip_inline_markdown(' '.join(para))
        para.clear()
        return joined

    for raw in content.splitlines():
        line = raw.rstrip()

        # HTML comment handling (covers the AUTO-GENERATED banner).
        if not in_fence:
            if in_comment:
                if _RE_HTML_COMMENT_CLOSE.search(line):
                    in_comment = False
                continue
            if _RE_HTML_COMMENT_OPEN.search(line):
                if not _RE_HTML_COMMENT_CLOSE.search(line):
                    in_comment = True
                continue

        # Code fence handling — ``` opens / closes a fenced block.
        if _RE_FENCE.match(line):
            in_fence = not in_fence
            flushed = flush()
            if flushed:
                yield flushed
            continue
        if in_fence:
            continue

        # Admonition block handling — ``!!! note`` followed by indented body.
        if in_admon:
            if not line.strip():
                in_admon = False
            elif line.startswith(' ') or line.startswith('\t'):
                continue
            else:
                in_admon = False
        if _RE_ADMONITION_START.match(line):
            flushed = flush()
            if flushed:
                yield flushed
            in_admon = True
            continue

        # Non-prose lines.
        if not line.strip():
            flushed = flush()
            if flushed:
                yield flushed
            continue
        if _RE_HEADING.match(line):
            flushed = flush()
            if flushed:
                yield flushed
            continue
        if _RE_TABLE_LINE.match(line) or _RE_BULLET.match(line) or _RE_BLOCKQUOTE.match(line):
            flushed = flush()
            if flushed:
                yield flushed
            continue

        para.append(line.strip())

    flushed = flush()
    if flushed:
        yield flushed


def _extract_summary(content: str, *, max_chars: int = 240) -> str:
    """Return a short, plain-text summary of a markdown document.

    Walks the paragraphs returned by ``_iter_prose_paragraphs`` and
    returns the first one that is meaningful prose (non-empty after
    inline-markdown stripping). Clips to ``max_chars``.
    """
    for para in _iter_prose_paragraphs(content):
        if not para:
            continue
        if len(para) > max_chars:
            clip = para[:max_chars].rsplit(' ', 1)[0]
            return f'{clip}…'
        return para
    return ''


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

def _doc_path_to_url(doc_path: str, base_url: str, use_directory_urls: bool) -> str:
    """Convert a docs-relative .md path into a public URL."""
    base = base_url.rstrip('/')
    rel = doc_path.lstrip('./').lstrip('/')
    if not rel.endswith('.md'):
        return f'{base}/{rel}'
    if use_directory_urls:
        if rel.endswith('/index.md'):
            url_path = rel[: -len('/index.md')] + '/'
        elif rel == 'index.md':
            url_path = ''
        else:
            url_path = rel[: -len('.md')] + '/'
    else:
        url_path = rel[: -len('.md')] + '.html'
    return f'{base}/{url_path}'


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render_llms_txt(
    cfg: dict, leaves: list[NavLeaf], base_url: str, use_directory_urls: bool,
) -> str:
    site_name = cfg.get('site_name') or 'OctoPwn'
    site_desc = (cfg.get('site_description') or '').strip()

    docs_dir = DOCS_ROOT / cfg.get('docs_dir', 'docs')

    lines: list[str] = []
    lines.append(f'# {site_name}')
    lines.append('')
    if site_desc and site_desc.lower() != site_name.lower():
        lines.append(f'> {site_desc}')
        lines.append('')

    lines.append(
        '> OctoPwn is a browser-based offensive-security toolkit covering '
        'discovery, authentication, AD enumeration, exploitation, '
        'credential cracking and NTLM relay attacks. The docs below '
        'cover the client plugins, network scanners, post-auth attacks, '
        'utility tools, relay servers, and the visual flowgraph '
        'automation framework.'
    )
    lines.append('')
    lines.append(
        '> This `llms.txt` is auto-generated from the mkdocs nav. Run '
        '`python scripts/generate_llms_txt.py` from the docs repo to '
        'regenerate after any nav / page change.'
    )
    lines.append('')

    # Group leaves by section, preserving nav order.
    grouped: dict[str, list[NavLeaf]] = {}
    section_order: list[str] = []
    for leaf in leaves:
        if leaf.section not in grouped:
            grouped[leaf.section] = []
            section_order.append(leaf.section)
        grouped[leaf.section].append(leaf)

    for section in section_order:
        lines.append(f'## {section}')
        lines.append('')
        current_subsection: str | None = None
        for leaf in grouped[section]:
            if leaf.subsection and leaf.subsection != current_subsection:
                lines.append('')
                lines.append(f'### {leaf.subsection}')
                lines.append('')
                current_subsection = leaf.subsection
            elif not leaf.subsection and current_subsection is not None:
                current_subsection = None

            doc_path = leaf.doc_path
            full_path = docs_dir / doc_path
            summary = ''
            if full_path.is_file():
                try:
                    summary = _extract_summary(full_path.read_text(encoding='utf-8'))
                except Exception as exc:  # noqa: BLE001
                    print(f'[!] Could not extract summary from {full_path}: {exc}',
                          file=sys.stderr)
            url = _doc_path_to_url(doc_path, base_url, use_directory_urls)
            if summary:
                lines.append(f'- [{leaf.title}]({url}): {summary}')
            else:
                lines.append(f'- [{leaf.title}]({url})')
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def _render_llms_full_txt(
    cfg: dict, leaves: list[NavLeaf], base_url: str, use_directory_urls: bool,
) -> str:
    site_name = cfg.get('site_name') or 'OctoPwn'
    docs_dir = DOCS_ROOT / cfg.get('docs_dir', 'docs')

    out: list[str] = []
    out.append(f'# {site_name} — full documentation bundle')
    out.append('')
    out.append(
        '> This file concatenates every page referenced from the mkdocs '
        'nav, in nav order. It is auto-generated by '
        '`scripts/generate_llms_txt.py --full`. For a curated index see '
        '`llms.txt`.'
    )
    out.append('')

    for leaf in leaves:
        full_path = docs_dir / leaf.doc_path
        if not full_path.is_file():
            continue
        url = _doc_path_to_url(leaf.doc_path, base_url, use_directory_urls)
        section_label = leaf.section
        if leaf.subsection:
            section_label = f'{leaf.section} / {leaf.subsection}'
        out.append('---')
        out.append('')
        out.append(f'# [{section_label}] {leaf.title}')
        out.append('')
        out.append(f'Source: {url}')
        out.append('')
        try:
            body = full_path.read_text(encoding='utf-8')
        except Exception as exc:  # noqa: BLE001
            out.append(f'[!] Could not read {full_path}: {exc}')
            out.append('')
            continue
        out.append(body.rstrip())
        out.append('')

    return '\n'.join(out).rstrip() + '\n'


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--mkdocs-yml',
        type=Path,
        default=MKDOCS_YML,
        help='Path to mkdocs.yml (default: %(default)s)',
    )
    parser.add_argument(
        '--base-url',
        default=None,
        help=(
            'Override the canonical site URL. If omitted, uses '
            '`site_url` from mkdocs.yml or '
            f'{DEFAULT_BASE_URL} as a fallback.'
        ),
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Also write docs/llms-full.txt (concatenation of every page).',
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.mkdocs_yml.is_file():
        print(f'[!] mkdocs.yml not found: {args.mkdocs_yml}', file=sys.stderr)
        return 2

    cfg = _load_mkdocs_config(args.mkdocs_yml)

    base_url = (
        args.base_url
        or cfg.get('site_url')
        or DEFAULT_BASE_URL
    )
    use_directory_urls = bool(cfg.get('use_directory_urls', True))

    leaves = _walk_nav(cfg.get('nav') or [])
    if not leaves:
        print('[!] mkdocs.yml has an empty / unreadable nav.', file=sys.stderr)
        return 2

    docs_dir = DOCS_ROOT / cfg.get('docs_dir', 'docs')

    llms_txt = _render_llms_txt(cfg, leaves, base_url, use_directory_urls)
    llms_path = docs_dir / 'llms.txt'
    llms_path.write_text(llms_txt, encoding='utf-8')
    print(f'[+] wrote {llms_path.relative_to(DOCS_ROOT)} '
          f'({len(leaves)} pages, {len(llms_txt)} bytes)')

    if args.full:
        full_txt = _render_llms_full_txt(cfg, leaves, base_url, use_directory_urls)
        full_path = docs_dir / 'llms-full.txt'
        full_path.write_text(full_txt, encoding='utf-8')
        print(f'[+] wrote {full_path.relative_to(DOCS_ROOT)} '
              f'({len(full_txt):,} bytes)')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
