#!/usr/bin/env python3
"""
Generate the per-category flowgraph block reference pages under
``docs/plugins/automations/flowgraph/blocks/`` directly from the live
``BLOCK_REGISTRY`` defined in
``octopwn/enterprise/flowgraph/registry.py``.

The generated pages are the canonical reference for every block type the
flowgraph engine knows about — ports, parameters, output schemas and
MITRE ATT&CK technique tags. They are regenerated on every release so the
docs cannot drift away from the registry.

Usage:
    cd octopwn-wasm-documentation
    python scripts/generate_flowgraph_reference.py

The script expects to find the octopwn package one level up
(``../octopwn``). Override with the ``--octopwn-root`` flag if you keep
the repos in a different layout.

Generated files start with an HTML banner so editors do not hand-edit
them by accident.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

# ---------------------------------------------------------------------------
# CLI + bootstrap
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
DOCS_ROOT = HERE.parent
DEFAULT_OCTOPWN_ROOT = (DOCS_ROOT.parent / 'octopwn').resolve()
BLOCKS_DIR = DOCS_ROOT / 'docs' / 'plugins' / 'automations' / 'flowgraph' / 'blocks'


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--octopwn-root',
        type=Path,
        default=DEFAULT_OCTOPWN_ROOT,
        help='Path to the octopwn checkout (default: %(default)s)',
    )
    parser.add_argument(
        '--out',
        type=Path,
        default=BLOCKS_DIR,
        help='Output directory for the generated block reference pages',
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Category configuration
# ---------------------------------------------------------------------------

# Each entry maps an output filename to the list of registry categories it
# contains, plus a title and a hand-written intro paragraph. Categories
# bundled together share the same page when they are functionally related
# (e.g. QUEUE + SINK + TAP + CONSOLE all act as terminal / pass-through
# blocks for items leaving a pipeline).
# Each page entry also has a ``summary`` field — a single short sentence
# rendered on the block-reference landing page (``blocks/index.md``).
PAGES: list[dict] = [
    {
        'file': 'sources.md',
        'title': 'Sources & prompts',
        'categories': ['SOURCE', 'PROMPT_SOURCE'],
        'summary': (
            'Inject credentials, targets, sessions or interactive prompts '
            'into the pipeline.'
        ),
        'intro': (
            'Source blocks inject data into a flowgraph. Most pipelines '
            'start with one or more `SOURCE_*` blocks that emit '
            'credentials, targets, or live sessions from the OctoPwn '
            'project store. `*_NEW` variants only emit items not yet '
            'processed in the current runloop iteration and are the '
            'building blocks of feedback loops — pair them with the '
            'matching `*_QUEUE` sink in [queues & sinks](queues-sinks.md). '
            '`PROMPT_SOURCE_*` blocks ask the operator for a value via a '
            'UI dialog at run time and are intended for tutorial / '
            'demo graphs.'
        ),
    },
    {
        'file': 'queues-sinks.md',
        'title': 'Queues, sinks, taps and console',
        'categories': ['QUEUE', 'SINK', 'TAP', 'CONSOLE'],
        'summary': (
            'Terminate pipelines, feed items back into the next runloop '
            'iteration, log items inline, or trigger another engine pass.'
        ),
        'intro': (
            '`QUEUE` blocks are feedback sinks: items wired into a queue '
            'are held for the *next* runloop iteration, where the '
            'matching `SOURCE_*_NEW` block re-emits them with their '
            '"seen" flag cleared. This is how a flowgraph discovers new '
            'credentials, queues them, and tries them again on the next '
            'pass without manual intervention.\n\n'
            '`SINK` blocks are terminators — `TERMINATOR_SINK` silently '
            'discards items, `FILE_SINK` writes them as JSONL, and the '
            '`RERUN_TRIGGER` family schedules another engine pass.\n\n'
            '`TAP_SINK` is a pass-through probe used to inspect what is '
            'flowing through a wire from the results panel. `CONSOLE` '
            'does the same plus a formatted log line per item.'
        ),
    },
    {
        'file': 'credmux.md',
        'title': 'CredMux',
        'categories': ['CREDMUX'],
        'summary': (
            'Routes a single credential stream onto protocol-typed '
            'output ports so each downstream block only sees credentials '
            'it can use.'
        ),
        'intro': (
            '`CREDMUX` is the single most important routing block: it '
            'fans a single `credential` stream out onto protocol-typed '
            'output ports so that each downstream scanner / session / '
            'attack block receives only credentials it can actually use. '
            'Wiring `SOURCE_CREDENTIALS → CREDMUX → SCANNER_SMBLOGIN.credential` '
            'is idiomatic. See the '
            '[typing & wiring guide](../typing-and-wiring.md) for the '
            'full list of `credential_*` wire types.'
        ),
    },
    {
        'file': 'filters.md',
        'title': 'Filters, gates and collectors',
        'categories': ['FILTER'],
        'summary': (
            'Conditional routing, flow gating, deduplication and '
            'port-gating of items as they move through the graph.'
        ),
        'intro': (
            'Filter blocks evaluate conditions on flowing items. '
            '`FILTER` and `FILTER_TARGETS` route items between `match` '
            'and `no_match` outputs based on a key / op / value triple. '
            '`COLLECT` accumulates items into a re-emittable store that '
            'feeds the `lookup` port of FILTER for set-membership '
            'checks. `GATE` is a flow-control toggle. `PAIR_DEDUP` '
            'cross-products targets × credentials and emits only `(tid, '
            'cid)` pairs not yet seen this runloop. `PORT_GATE` only '
            'lets targets through that have a given port open, running '
            'an automatic portscan if no port data exists yet.'
        ),
    },
    {
        'file': 'scanners.md',
        'title': 'Scanners',
        'categories': ['SCANNER'],
        'summary': (
            'One block per entry in `OCTOPWN_SCANNER_TABLE` — '
            'all OctoPwn scanners exposed as flowgraph nodes.'
        ),
        'intro': (
            'Every entry in `octopwn.scanners.OCTOPWN_SCANNER_TABLE` is '
            'auto-registered as a `SCANNER_<NAME>` block. Scanner blocks '
            'have a `target` input port, an optional `credential` port '
            '(for authenticated scanners), an optional `pair` input that '
            'bypasses the cross-product, and a `result` output that '
            'emits scan-result items. Family-specific params (dialect, '
            'protocol, port lists, …) are derived dynamically from '
            '`octopwn.common.scanparams` so they always reflect what '
            'the scanner itself accepts. For the full scanner catalogue '
            '(WASM compat, tier, etc.) see the '
            '[scanner overview](../../../scanners/index.md).'
        ),
    },
    {
        'file': 'sessions.md',
        'title': 'Sessions and ID splitters',
        'categories': ['SESSION'],
        'summary': (
            'Open authenticated client sessions and unpack session / '
            'error items back into typed target + credential streams.'
        ),
        'intro': (
            '`OPEN_SESSION_<CLIENT>` blocks consume a `target` (and a '
            'protocol-typed `credential` where required) and emit a '
            '`session_<client>` reference on success or an `error` dict '
            'on failure. One block is generated per entry in '
            '`octopwn.clients.OCTOPWN_CLIENT_TABLE`. The `result` input '
            'port accepts a combined scan-result with both `__tid` and '
            '`__cid` set (typically straight out of an authenticated '
            'scanner like `SCANNER_SMBADMIN`) and opens exactly one '
            'session per item.\n\n'
            '`ID_SPLITTER` and `ID_SPLITTER_PAIR` unpack a session or '
            'error item back into target / credential identifiers so '
            'downstream attack blocks can be wired without losing '
            'provenance. Prefer `ID_SPLITTER_PAIR` whenever each '
            '(target, credential) pair should run an attack exactly '
            'once.'
        ),
    },
    {
        'file': 'commands.md',
        'title': 'Session commands',
        'categories': ['COMMAND'],
        'summary': (
            'Run any client command (LDAP, SMB, RDP, …) over a live '
            'session — the same surface as the interactive console.'
        ),
        'intro': (
            'A `CMD_<CLIENT>` block runs any command supported by a '
            'live `<CLIENT>` session — the command list comes straight '
            'from the same command map that drives the interactive '
            'console for that client. One block is generated per entry '
            'in `OCTOPWN_CLIENT_TABLE`. Wire the optional `data` input '
            'to feed dynamic per-invocation arguments (e.g. one share '
            'name per item) from an upstream scanner.'
        ),
    },
    {
        'file': 'attacks.md',
        'title': 'Attacks',
        'categories': ['ATTACK'],
        'summary': (
            'Curated, opinionated wrappers around the most common post-'
            'auth attacks (Kerberoast, DCSync, DPAPI, ADCS ESC1/4, …).'
        ),
        'intro': (
            'Curated, opinionated wrappers around the most common '
            'post-auth attacks in `OCTOPWN_ATTACK_TABLE`. Most attack '
            'blocks accept either a `pair` input (paired target + '
            'credential dict from `ID_SPLITTER_PAIR`) or independent '
            '`target` and `credential` inputs that are cross-producted '
            'internally. Successful runs emit `scan_result` items and '
            'auto-store any discovered credentials in the OctoPwn '
            'credential store, where they become available to '
            'downstream `SOURCE_CREDENTIALS_NEW` blocks.'
        ),
    },
    {
        'file': 'enumeration.md',
        'title': 'Enumeration',
        'categories': ['ENUMERATION'],
        'summary': (
            'Stream domain objects (users, computers, ADCS templates, '
            'trusts) from an open LDAP session.'
        ),
        'intro': (
            'LDAP enumeration blocks consume an open `session_ldap` and '
            'stream individual user / computer / template / trust dicts '
            'to downstream blocks. The engine uses `StorageRef` so the '
            'memory footprint stays flat even on 100 000-user '
            'domains — items are pulled lazily from the on-disk SQLite '
            'store the LDAP client already maintains for audit trails. '
            'A typical chain is `ENUM_LDAP_COMPUTERS → '
            'TARGET_QUEUE` to feed discovered hostnames into the next '
            'runloop pass.'
        ),
    },
    {
        'file': 'transforms.md',
        'title': 'Transforms',
        'categories': ['TRANSFORM'],
        'summary': (
            'Convert credentials from one form to another — PKINIT U2U '
            'PFX → NT hash, hashcat wordlist / mask cracking.'
        ),
        'intro': (
            'Transform blocks take credentials of one kind and turn '
            'them into credentials of another kind. `CONVERT_PFX_TO_NT` '
            'walks a PKINIT U2U exchange on an already-opened Kerberos '
            'session to extract an NT hash. The `HASHCAT_*` blocks '
            'spawn a visible HASHCAT utility session, auto-detect the '
            'hash type from the incoming credential, and emit '
            'plaintext-password credentials on success.'
        ),
    },
    {
        'file': 'script.md',
        'title': 'Script',
        'categories': ['SCRIPT'],
        'summary': (
            'Drop a user-authored Python coroutine into the middle of a '
            'pipeline when the built-in vocabulary is not enough.'
        ),
        'intro': (
            'The `SCRIPT` block lets you drop a Python coroutine into '
            'the middle of a flowgraph for the cases where the existing '
            'filter / transform vocabulary is not enough. See the '
            '[script block guide](../script-block.md) for the '
            '`process(item, octopwn)` contract and a couple of worked '
            'examples.'
        ),
    },
    {
        'file': 'composite.md',
        'title': 'Composites and boundaries',
        'categories': ['BOUNDARY'],
        'summary': (
            'Boundary blocks used to define the external port surface '
            'of reusable, named composite sub-flowgraphs.'
        ),
        'intro': (
            'Composite blocks let you turn a piece of a flowgraph into '
            'a reusable, named component with its own typed ports — '
            'think "save selection as block". The composite itself is '
            'an inner `Flowgraph` whose external interface is defined '
            'by the boundary nodes documented below. See the '
            '[composites guide](../composites.md) for the full '
            'authoring / saving / sharing workflow.'
        ),
    },
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

BANNER = (
    '<!--\n'
    'AUTO-GENERATED — DO NOT EDIT BY HAND.\n'
    'Regenerate via:\n'
    '    python scripts/generate_flowgraph_reference.py\n'
    'Source of truth: octopwn/enterprise/flowgraph/registry.py.\n'
    '-->\n'
)

_MD_ESCAPE = str.maketrans({'|': '\\|', '\n': ' '})


def _md_escape(text) -> str:
    if text is None:
        return ''
    return str(text).translate(_MD_ESCAPE).strip()


def _yesno(b) -> str:
    return 'yes' if b else 'no'


def _format_default(value) -> str:
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        if value == '':
            return '""'
        return f'`{value}`'
    return f'`{value}`'


def _render_ports(block) -> str:
    if not block.ports:
        return '*No ports.*\n'
    lines = [
        '| Port | Direction | Type | Optional | Description |',
        '|------|-----------|------|----------|-------------|',
    ]
    for p in block.ports:
        lines.append(
            f'| `{_md_escape(p.name)}` | {p.direction} | `{_md_escape(p.type_name)}` | '
            f'{_yesno(p.optional)} | {_md_escape(p.description)} |'
        )
    return '\n'.join(lines) + '\n'


def _render_params(block) -> str:
    if not block.params:
        return '*No parameters.*\n'
    lines = [
        '| Parameter | Type | Default | Required | Description |',
        '|-----------|------|---------|----------|-------------|',
    ]
    for p in block.params:
        lines.append(
            f'| `{_md_escape(p.name)}` | `{_md_escape(p.type_name)}` | '
            f'{_format_default(p.default)} | {_yesno(p.required)} | '
            f'{_md_escape(p.description)} |'
        )
    return '\n'.join(lines) + '\n'


def _render_output_schema(block) -> str:
    if not block.output_schema:
        return ''
    out: list[str] = []
    for port_name, fields in block.output_schema.items():
        if not fields:
            continue
        out.append(f'**Output schema — `{port_name}`**\n')
        out.append('| Field | Type | Description |')
        out.append('|-------|------|-------------|')
        for f in fields:
            out.append(
                f'| `{_md_escape(f.name)}` | `{_md_escape(f.type_name)}` | '
                f'{_md_escape(f.description)} |'
            )
        out.append('')
    return '\n'.join(out) + '\n' if out else ''


def _render_attack_techniques(block) -> str:
    techs = getattr(block, 'attack_techniques', None) or []
    if not techs:
        return ''
    badges = ' '.join(f'`{t}`' for t in techs)
    return f'**MITRE ATT&CK:** {badges}\n'


def _render_block(block) -> str:
    parts: list[str] = []
    parts.append(f'### `{block.id}`\n')
    parts.append(f'*Category: `{block.category}`*\n')
    if block.description:
        parts.append(f'{block.description}\n')
    parts.append('**Ports**\n')
    parts.append(_render_ports(block))
    parts.append('**Parameters**\n')
    parts.append(_render_params(block))
    schema = _render_output_schema(block)
    if schema:
        parts.append(schema)
    techs = _render_attack_techniques(block)
    if techs:
        parts.append(techs)
    return '\n'.join(parts)


def _render_page(page: dict, blocks_by_category: dict) -> str:
    blocks: list = []
    for cat in page['categories']:
        for block in blocks_by_category.get(cat, []):
            # Skip user-installed composites — they live in
            # ~/.octopwn/composites/ and are not part of the framework
            # reference.
            if block.category == 'COMPOSITE':
                continue
            blocks.append(block)

    out: list[str] = [
        BANNER,
        f'# {page["title"]}\n',
        page['intro'] + '\n',
        '---\n',
    ]
    if not blocks:
        out.append('*No blocks in this category.*\n')
        return '\n'.join(out)

    out.append(f'**{len(blocks)} block type(s) in this category.**\n')
    out.append('---\n')

    for block in blocks:
        out.append(_render_block(block))
        out.append('---\n')

    return '\n'.join(out)


def _render_index(blocks_by_category: dict, page_specs: list[dict]) -> str:
    total = sum(
        len([b for b in blocks_by_category.get(c, []) if b.category != 'COMPOSITE'])
        for page in page_specs
        for c in page['categories']
    )
    out: list[str] = [
        BANNER,
        '# Block reference\n',
        (
            f'Complete, auto-generated reference for the **{total}** block '
            'types the flowgraph engine knows about. Regenerated from '
            '`octopwn/enterprise/flowgraph/registry.py` on every '
            'release — see the comment at the top of each page for the '
            'regeneration command.\n'
        ),
        (
            'For the high-level mental model, start with the '
            '[core concepts](../concepts.md) page; for examples that '
            'wire these blocks together end-to-end, see the '
            '[recipes](../recipes/index.md).\n'
        ),
        '## Pages\n',
    ]
    for page in page_specs:
        cats = ', '.join(f'`{c}`' for c in page['categories'])
        count = sum(
            1 for c in page['categories']
            for b in blocks_by_category.get(c, [])
            if b.category != 'COMPOSITE'
        )
        out.append(
            f'### [{page["title"]}]({page["file"]}) — {count} block(s)\n'
        )
        out.append(f'{page["summary"]}\n')
        out.append(f'*Covers categories: {cats}.*\n')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = _parse_args()

    if not args.octopwn_root.is_dir():
        print(
            f'[!] --octopwn-root does not exist: {args.octopwn_root}',
            file=sys.stderr,
        )
        return 2

    sys.path.insert(0, str(args.octopwn_root))

    try:
        from octopwn.enterprise.flowgraph.registry import BLOCK_REGISTRY
    except Exception as exc:
        print(f'[!] Failed to import BLOCK_REGISTRY: {exc}', file=sys.stderr)
        return 2

    blocks_by_category: dict = {}
    for block in BLOCK_REGISTRY.values():
        blocks_by_category.setdefault(block.category, []).append(block)

    args.out.mkdir(parents=True, exist_ok=True)

    written = 0
    for page in PAGES:
        body = _render_page(page, blocks_by_category)
        target = args.out / page['file']
        target.write_text(body, encoding='utf-8')
        written += 1
        print(f'[+] wrote {target.relative_to(DOCS_ROOT)}')

    # Auto-generated index landing
    index_target = args.out / 'index.md'
    index_target.write_text(
        _render_index(blocks_by_category, PAGES),
        encoding='utf-8',
    )
    written += 1
    print(f'[+] wrote {index_target.relative_to(DOCS_ROOT)}')

    # Sanity check: report any category that we did not route to a page
    routed = {c for page in PAGES for c in page['categories']}
    routed.add('COMPOSITE')  # user composites are intentionally excluded
    unrouted = sorted(set(blocks_by_category) - routed)
    if unrouted:
        print(
            f'[!] Categories present in registry but not routed to a page: '
            f'{unrouted}',
            file=sys.stderr,
        )

    print(f'[+] {written} file(s) written under {args.out.relative_to(DOCS_ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
