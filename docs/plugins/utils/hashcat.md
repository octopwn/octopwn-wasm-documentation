# Hashcat Utility

The **Hashcat** utility wraps a **local** [Hashcat](https://hashcat.net/)
binary and ties it into OctoPwn's [Credentials Hub](../../user-guide/credentials.md):
hashes added to the Hub are queued for cracking automatically, and any plain
recovered by Hashcat is fed back into the Hub as a new `PASSWORD` credential
linked to the original.

The util does **not** ship Hashcat itself. You point it at the Hashcat
binary and at a wordlist (and optionally a rules file) and the rest is
plumbing.

!!! warning "Server-side / Enterprise only"
    Hashcat is a native binary that needs a real OS process and (usually)
    GPU access. The cracking commands **do not work in the WASM build** —
    they explicitly say so when invoked. Use this utility from the
    Enterprise / server build, or accept that you'll only ever use it for
    its potfile / cred-merge bookkeeping.

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `hashcat` | `hashcat` | Path to the Hashcat binary. Must be executable on the OctoPwn host. |
| `wordlist` | `rockyou.txt` | Path to the wordlist used by `wordlist`-mode runs. |
| `rules` | none | Optional rules file (`-r`). |
| `maxruntime` | `5` | Per-run timeout in **minutes**. Hashcat is killed when it expires. |
| `brutemask` | `?a?a?a?a?a?a?a` | Mask used by `bruteforce` runs (Hashcat `-a 3`). |
| `brutemin` | `1` | Increment-min for masked runs. |
| `brutemax` | `7` | Increment-max for masked runs. |
| `autoattacktype` | `wordlist` | Default attack type for autocrack — `wordlist` or `bruteforce`. |
| `hashtypes` | `all` | Either `all` or a list of Hashcat hash type IDs (or alias names) to accept; everything else is skipped. |

---

## Hash type recognition

The utility carries a small alias table for the credential `stype` values
OctoPwn produces internally:

| OctoPwn `stype` | Hashcat `-m` |
| --- | --- |
| `MD5` | `0` |
| `NTLM` / `NT` | `1000` |
| `LM` | `3000` |
| `NETNTLMV2` | `5600` |
| `NETNTLMV1` | `5500` |

Kerberos credentials are recognised from their string prefix and routed
to the right `-m`:

| Secret starts with | Mode | Origin |
| --- | --- | --- |
| `$krb5tgs$23$` | `13100` | Kerberoast (RC4) |
| `$krb5asrep$23$` | `18200` | AS-REP roast (RC4) |
| `$krb5tgs$17$` / `$18$` | `19600` / `19700` | Kerberoast (AES128 / AES256) |
| `$krb5pa$17$` / `$18$` | `19800` / `19900` | Kerberos pre-auth (AES128 / AES256) |

If a credential's `stype` is already a numeric Hashcat mode (e.g. `13100`),
that's used as-is. Anything else is logged and skipped — see
[`hashtypes`](#parameters) above to pre-filter what you want auto-cracked.

---

## Commands

### GENERIC

#### potfile
`potfile(filepath)` — load a Hashcat potfile (the `hash:plain` format that
Hashcat writes when it cracks). Each line is parsed; `$HEX[...]` plains are
hex-decoded back into UTF-8.

This **does not** add credentials yet — it only loads the potfile into the
session's lookup table. Call [`addcreds`](#addcreds) afterwards to merge
the potfile into the Hub.

#### addcreds
`addcreds()` — for every credential in the Hub whose secret matches a hash
in the loaded potfile, create a new `PASSWORD` credential with the cracked
plain (and the same domain / username / SID metadata as the original).
Duplicates are skipped via the credential checksum mechanism.

This is the typical "import results from a previous Hashcat run" path.

#### sethashcat
`sethashcat(path)` — change the path to the Hashcat binary. Must point at
an existing file. Equivalent to `setparam hashcat <path>` but with an
existence check.

#### test
`test()` — sanity-test the Hashcat install by cracking the well-known empty
NT hash (`31d6cfe0d16ae931b73c59d7e0c089c0`) against the configured
wordlist.

### LOCAL

#### localcrack
`localcrack(hashtype, hashvalue, wordlist, rules=None, maxruntime=5)` — fire
a one-shot Hashcat run against a single hash. Useful for quickly checking
whether a hash you just typed in is in your wordlist; not the typical
workflow (use [`autocrack`](#autocrack) for the streaming-into-the-Hub
workflow).

### AUTOCRACK

#### autocrack
`autocrack()` — register a credential handler with the OctoPwn core. From
this point on, **every new credential** added to the Hub is inspected:

- If its `stype` (or detected Kerberos prefix) is in the configured
  `hashtypes` list, it goes into a per-mode buffer.
- A worker task drains the buffer in 5-second batches and runs Hashcat
  per batch using the configured wordlist + rules + `maxruntime`.
- Any cracked plain comes back through the standard cred-merge path —
  the original hashed credential gets a sibling `PASSWORD` credential
  with the same identity metadata.

This is the headline workflow: kick off a kerberoast, leave the project
running, and the cracked passwords appear in the Hub on their own.

#### disableautocrack
Tear down the credential handler. Already-running cracks finish; new
credentials are no longer queued.

#### stopautocrack
Drop the current autocrack queue. Hashes already in flight are not
killed; the queue is just emptied so they don't get re-queued on the next
batch.

---

## Operational notes

- **`maxruntime` is per Hashcat invocation.** When autocrack groups, say,
  ten kerberoast hashes into one batch, the whole batch runs for one
  `maxruntime` window. Pick a value that's long enough for your wordlist
  but short enough to not block the next batch.
- **One worker, sequential batches.** The worker runs one Hashcat at a
  time. There is no parallelism inside the util — Hashcat itself uses all
  the GPU you give it.
- **Output parsing is the standard `hash:plain` Hashcat output**, with
  `--quiet -O` flags. The util reads stdout line by line; if Hashcat is
  configured to emit a different format (potfile-only, JSON, etc.) the
  parser will skip the lines.
- **Cracked plains land as new credentials, not modifications.** The
  original NT / kerberoast credential is preserved; the new
  `PASSWORD` credential is linked through matching domain / username /
  SID. Filter the Hub by `description = HASHCAT` to see everything the
  util has produced.

---

## See also

- [Pypykatz utility](pypykatz.md) — the source of many of the NT / kirbi
  credentials Hashcat will end up cracking.
- [`KERBEROAST`](../attacks/kerberoast.md) /
  [`TIMEROAST`](../attacks/timeroast.md) /
  [`IPMIHASH`](../attacks/ipmihash.md) — generators of Kerberos / NTP /
  IPMI hashes that this utility will pick up via autocrack.
- [Credentials Hub](../../user-guide/credentials.md) — the autocrack
  workflow lives entirely on top of the Hub.
- [Hashcat hash modes reference](https://hashcat.net/wiki/doku.php?id=example_hashes) —
  for every `stype` not listed in the alias table above.
