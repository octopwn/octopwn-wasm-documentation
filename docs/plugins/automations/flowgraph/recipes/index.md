# Recipes

Six small, self-contained recipes that show how the blocks in the
[block reference](../blocks/index.md) snap together into real
pipelines. Each one fits on one screen, is wired to actually validate
against the engine, and ends in something useful — discovered shares,
cracked hashes, a kill-chain entry.

| Recipe                                                            | Teaches |
|-------------------------------------------------------------------|---------|
| [Portscan + SMB finger](portscan-smbfinger.md)                    | The simplest possible chain. Targets in, structured results out. |
| [Credential spray](credential-spray.md)                           | CREDMUX, cross-product semantics, FILTER on result fields. |
| [DCSync from creds](dcsync-from-creds.md)                         | Cross-product on `OPEN_SESSION_*`, CMD_DCSYNC, CREDENTIAL_QUEUE feedback. |
| [Kerberoast and crack](kerberoast-and-crack.md)                   | Output → transform → queue. ATT&CK badges in the kill chain. |
| [ADCS ESC1 to NT](adcs-esc1-to-nt.md)                             | Enumeration block, dataset wire type, CONVERT_PFX_TO_NT. |
| [Runloop convergence](runloop-discover-iterate.md)                | A self-feeding pipeline that uses `runloop` to walk itself to a fixed point. |

---

## How to use a recipe

Every recipe page follows the same template:

1. **Goal** — one sentence: what the pipeline produces.
2. **Pipeline** — a mermaid diagram of the wiring.
3. **Block-by-block walkthrough** — what each block contributes and
   what params matter, linking back to the block reference.
4. **Saved graph JSON** — the actual JSON you can copy into a file
   and load with `loadfile`.
5. **Variations** — sensible tweaks (different scope, opsec
   tightening, alternative transforms).

You should usually:

- Read through the recipe in the docs.
- Drop the JSON into a `.json` file under `/tmp/` or your engagement
  workdir.
- `createutil FLOWGRAPH` and `loadfile` the JSON.
- Open the FLOWGRAPH window to inspect the loaded graph — node
  positions are encoded in the JSON so the layout matches the
  mermaid diagram.
- Adjust `targets` / `credentials` / params in the config panel to
  your scope, then hit Run.

The recipes are deliberately minimal — they teach a *pattern*, not a
turnkey engagement script. Composite-ising them and chaining them is
left to the [composites](../composites.md) page.
