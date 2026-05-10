# Pypykatz Utility

This is OctoPwn's bundled wrapper around
[Pypykatz](https://github.com/skelsec/pypykatz) — the Python re-implementation
of `mimikatz`. It performs **offline parsing** of credential-bearing files
that you've already gathered (LSASS minidumps, registry hives, NTDS.dit) and
provides a handful of ad-hoc decryptors and hash calculators.

It does **not** dump LSASS or registry hives by itself. To collect those
artefacts in the first place, see:

- [`SMBREGDUMP`](../attacks/smbregdump.md) / [`SMBREGDUMP2`](../attacks/smbregdump2.md) —
  remote SMB-side hive dumping (with and without touching disk).
- [`DPAPI` attack](../attacks/dpapi.md) — orchestrates SMB-side LSASS / SCCM
  / DPAPI vault collection; many of its outputs feed straight into the
  commands below.

Every credential discovered by these commands is **automatically added** to
the [Credentials Hub](../../user-guide/credentials.md) tagged with the
appropriate `stype` (`PASSWORD`, `NT`, `kirbib64`, `DPAPI`, `SHA1`,
`AES`, `MSV`, etc.).

---

## Commands

### LSASS

#### lsass
`lsass(minidumpfile, packages=None)` — parse an LSASS minidump and pull
secrets from every supported credential package (`msv`, `wdigest`, `ssp`,
`livessp`, `kerberos`, `dpapi`, `cloudap`). Each Kerberos ticket found is
turned into a base64 `kirbib64` credential in the Hub; classic password /
NT hashes land as `PASSWORD` / `NT`.

`packages` is reserved for future per-package filtering — currently the
underlying parser is invoked with `packages=['all']` regardless of input.

#### registry
`registry(system, sam=None, security=None, software=None)` — offline parse
of registry hives. The `SYSTEM` hive is mandatory (it holds the
boot key / LSA cache encryption keys); the others extract additional
secrets:

- `SAM` → local user NT hashes
- `SECURITY` → LSA secrets, cached domain logons, machine account secrets
- `SOFTWARE` → optional, used for some metadata

### NTDS

#### ntds
`ntds(systemhive, ntdsfile, outfile=auto)` — parse an extracted `NTDS.dit`
along with the matching `SYSTEM` hive (needed for the boot key). Streams
secrets into the Hub *and* into a CSV file (`outfile`, default
`ntds_secrets_<random>.txt`) in the working directory.

Includes **password history** when present (`with_history=True` is
hard-wired), so historical NT hashes are recovered too — useful for cracking
campaigns where users rotate to similar passwords.

!!! info "Where do I get NTDS.dit?"
    Use the [`SMBREGDUMP`](../attacks/smbregdump.md) /
    [`SMBREGDUMP2`](../attacks/smbregdump2.md) attacks against a Domain
    Controller (or do a `dcsync` instead — see
    [`DCSYNC`](../attacks/dcsync.md) — which avoids the file-copy step
    altogether).

### DECRYPTORS

#### gppassword
`gppassword(pw_enc_b64)` — decrypt the legacy Group Policy Preferences
"cpassword" attribute. Pure local-only, no network calls.

#### ofscan
`ofscan(encdata_or_file)` — decrypt password-style values found in
TrendMicro OfficeScan's `ofcscan.ini`. Accepts either a raw encrypted blob
or a path to the file.

### HASHING

These are pure local hash calculators — handy when you need to feed a hash
directly into another tool without the round-trip of authenticating
somewhere first.

#### nt
NT hash of a plaintext password.

#### lm
LM hash of a plaintext password.

#### msdcc
MS Domain Cached Credentials hash, **version 1** (legacy DCC).

#### msdcc2
MS Domain Cached Credentials hash, **version 2** (current MS-CACHE2 / DCC2).
Default iteration count is `10240` (Windows default); override with the
`iteration` argument if you're targeting a non-default config.

#### kerberos
`kerberos(username, password, domain=None)` — derive the four Kerberos
keys (`AES128`, `AES256`, `RC4-MD5`, `3DES`) from a password. AES keys
require `domain` because they salt with `<UPPER_DOMAIN><user>` in the
canonical case — and that salt **isn't always what you'd expect**: machine
accounts use `host<host>.<dnsdomain>`, some SPN-style accounts use
`<service>/<host>`, etc. If your AES key doesn't match what you see on the
wire, the salt is the first place to check.

#### hashes
`hashes(username, password, domain=None)` — all of the above in one go.

---

## Limitations and caveats

- **No live LSASS dump.** `do_locallsass` is a stub. Use the
  [`DPAPI` attack](../attacks/dpapi.md) (which orchestrates remote LSASS
  collection over SMB) or any external dumper of your choice and feed the
  minidump in via `lsass`.
- **NTDS.dit + SYSTEM must be from the same DC.** The boot key is
  per-machine; the SYSTEM hive of a different host won't decrypt the
  database.
- **All file paths are interpreted in OctoPwn's working directory** (the
  browser virtual filesystem on the WASM build, real filesystem on
  Enterprise). Upload your dumps there first.
- **Hash calculators are convenience helpers**, not a cracker. For actual
  cracking, see the [HASHCAT utility](hashcat.md).

---

## See also

- [DPAPI utility](dpapi.md) — the analytical layer on top of decrypted
  master keys (Chrome, WiFi, vault files, securestrings, CloudAP PRT, …).
- [DPAPI attack](../attacks/dpapi.md) — automates SMB-side collection of
  master keys and credential blobs.
- [`SMBREGDUMP`](../attacks/smbregdump.md) /
  [`SMBREGDUMP2`](../attacks/smbregdump2.md) — collect the registry hives
  this utility consumes.
- [HASHCAT utility](hashcat.md) — feed the hashes from `nt` / `msdcc2` /
  the LSASS / NTDS dumps directly into Hashcat.
