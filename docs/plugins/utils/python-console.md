# Python Console

The **Python Console** is an in-browser Python interpreter wired into the
OctoPwn UI. It is intended for **quick, one-off Python evaluation** — testing
a snippet, computing something on the fly, importing a module to inspect its
attributes, prototyping the body of a [plugin](pluginloader.md) before
formalising it.

It is not a full IDE — for that, see the [IDE utility](ide.md). It is not a
shell — for that, see the [Terminal utility](terminal.md). It is not a
remote interpreter either — the code runs **in the same Python interpreter
as OctoPwn itself**, with full access to the live `octopwnobj`, the
loaded credentials, the open sessions, and the project state.

---

## Limitations to know about up front

- **Synchronous.** The console is a classic REPL — it does not run in the
  asyncio event loop. Long-running code blocks the OctoPwn event loop
  while it runs. In the WASM build, long-running code freezes the
  browser tab. Keep snippets short.
- **`await` does not work** at the top level. To call coroutines, use
  `asyncio.get_event_loop().run_until_complete(...)` (server build only)
  or schedule them as tasks and inspect them later.
- **No isolation.** Anything you do in the console affects the running
  OctoPwn instance. Setting attributes on `octopwnobj`, mutating the
  Hub, closing sessions — all of it is real and persistent.
- **No persistence between sessions.** The console state is lost when the
  project is closed.

---

## When to use it

| You want to… | Use… |
| --- | --- |
| Run a few lines of Python against `octopwnobj` | Python Console |
| Author a reusable extension with autocompletion | [IDE utility](ide.md) |
| Drive a long-running, async task | [Plugin Loader](pluginloader.md) |
| Run a local OS command | [Terminal utility](terminal.md) |

---

## See also

- [IDE utility](ide.md) — full plugin development environment with
  autocompletion via the OctoPwn language server.
- [Plugin Loader](pluginloader.md) — the right home for any non-trivial
  Python you want to keep around.
- [Terminal utility](terminal.md) — when you want a shell, not a Python
  REPL.
