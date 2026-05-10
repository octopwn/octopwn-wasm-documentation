# Plugin Loader Utility

The **Plugin Loader** is the runtime that loads and runs **OctoPwn plugins** —
custom Python modules that extend OctoPwn at runtime without modifying the
core code base. It is the entry point for everything authored in the
[OctoPwn IDE](ide.md) and for any plugin shipped via the plugin distribution
mechanism (the `plugins.zip` bundle).

A plugin is, in the simplest form, a Python file that exports an
`OctoPwnPlugin` class with two coroutines:

```python
class OctoPwnPlugin:
    async def pluginsetup(self, name, octopwnobj, print_cb, client_id):
        # Stash references; register hooks; print banners; etc.
        ...

    async def run(self):
        # The actual plugin body. Runs as a long-lived asyncio task.
        ...
```

The util **does not** install plugins. Plugin files are managed by OctoPwn
itself — the loader simply imports and executes them.

---

## Plugin lifecycle

1. The loader resolves the plugin file path (either passed explicitly or
   looked up by name in the plugin folder for the active license).
2. The Python module is imported (`importlib.util.spec_from_file_location`).
3. `OctoPwnPlugin()` is instantiated.
4. `pluginsetup(...)` is awaited — this is the plugin's chance to wire up
   handlers, register session callbacks, etc.
5. `run()` is scheduled as an asyncio task. The plugin lives until the task
   completes or until the OctoPwn session is torn down.

There is no built-in stop / unload command. Plugins that should be stoppable
must implement their own shutdown signal (typically by checking a flag in
their `run()` loop).

---

## Commands

### GENERIC

#### load
`load(pluginname, plugin_file=None, is_auto=False)` — load a plugin by
**name**. The loader looks up the plugin in the project's plugin folder and
runs it. `plugin_file` and `is_auto` are typically left at their defaults;
they are used by the autoloader path below.

Each invocation gets a unique internal name (`<pluginname>-<counter>`) so
the same plugin can be loaded multiple times — useful for plugins that take
parameters and you want several concurrent instances.

#### autoload
`autoload()` — iterate over every plugin marked **autoload** for the current
project and load each one. Equivalent to calling `load` once per autoload
plugin. This is also what OctoPwn calls automatically at project startup
when the plugin loader util is started.

#### loaddev
`loaddev(pluginpath, pluginname=None)` — **development** flavour of `load`
that takes an arbitrary file system path instead of a managed plugin name.
Use this when iterating on a plugin in the OctoPwn IDE — point it at the
file you're editing and it will hot-load the new revision (a fresh
`OctoPwnPlugin` instance) without touching the managed plugin store.

!!! warning "loaddev is for development only"
    `loaddev` runs *any* Python file you point it at. Don't expose it to
    untrusted operators, and don't load files of unknown provenance — a
    plugin has the same access to the OctoPwn object as any built-in
    module (credentials, sessions, targets, network).

---

## Authoring plugins

A minimal plugin that prints "hello" once a minute:

```python
import asyncio


class OctoPwnPlugin:
    def __init__(self):
        self.octopwn = None
        self.print = None

    async def pluginsetup(self, name, octopwnobj, print_cb, client_id):
        self.octopwn = octopwnobj
        self.print = print_cb

    async def run(self):
        while True:
            await self.print('hello from a plugin')
            await asyncio.sleep(60)
```

For richer plugins (registering credential / session handlers, calling into
core modules, creating sessions on the fly) see the
[function stubs and language server](https://github.com/octopwn/octopwn-ide-language-server)
in the IDE — the stubs document the full `OctoPwnPlugin` contract and the
`octopwnobj` API surface.

---

## Limitations and caveats

- **No sandboxing.** Plugins run in the same Python interpreter as OctoPwn
  itself. They have full access to `octopwnobj` (credentials, sessions,
  targets) and to the host filesystem (subject to the WASM sandbox in the
  browser build).
- **No automatic reload.** Editing a plugin file does not re-run the plugin —
  invoke `loaddev` (dev) or stop and re-`load` (managed) to pick up changes.
- **`run()` is awaited as a task.** A plugin whose `run()` returns
  immediately is effectively a one-shot — that's fine, but be aware there's
  no way to "tick" a plugin from the loader after `run()` completes.
- **Errors during `pluginsetup` or `run` are printed to the session** but
  do not crash OctoPwn. Long-running plugins should `try/except` their main
  loop to avoid silently dying on transient errors.

---

## See also

- [IDE utility](ide.md) — the in-browser editor with autocompletion / stubs
  for authoring plugins.
- [Python console](python-console.md) — when a plugin is overkill and you
  just want to run a few lines of Python against `octopwnobj`.
- [OctoPwn IDE Language Server](https://github.com/octopwn/octopwn-ide-language-server) —
  the function stubs that define the plugin API.
